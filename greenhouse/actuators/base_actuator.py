import json
from datetime import datetime

import paho.mqtt.client as mqtt

from greenhouse.config import (
    BROKER_HOST,
    BROKER_KEEPALIVE,
    BROKER_PORT,
    QOS_CRITICAL,
    RETAIN_STATE,
)


class BaseActuator:
    def __init__(self, actuator_id: str, topic_cmd: str, topic_state: str) -> None:
        self.actuator_id = actuator_id
        self.topic_cmd = topic_cmd
        self.topic_state = topic_state
        self.state = "OFF"

        self.client = mqtt.Client(client_id=f"actuator_{actuator_id}")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{self.actuator_id}] ✅ Connecté au broker")
            client.subscribe(self.topic_cmd, qos=QOS_CRITICAL)
            print(f"[{self.actuator_id}] Abonné à {self.topic_cmd}")
            self.publish_state()
        else:
            print(f"[{self.actuator_id}] ❌ Échec connexion")

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"[{self.actuator_id}] ⚠️ Déconnexion inattendue")

    def _on_message(self, client, userdata, msg):
        try:
            raw = msg.payload.decode().strip()
            action = raw.upper()
            if raw.startswith("{"):
                action = json.loads(raw).get("action", "").upper()

            if action in ["ON", "OFF"]:
                self.state = action
                print(f"[{self.actuator_id}] Commande: {action}")
                self.execute_action(action)
                self.publish_state()
            else:
                print(f"[{self.actuator_id}] Commande invalide: {raw}")
        except Exception as exc:  # pragma: no cover
            print(f"[{self.actuator_id}] Erreur: {exc}")

    def execute_action(self, action: str) -> None:
        print(f"[{self.actuator_id}] Action: {action}")

    def publish_state(self) -> None:
        payload = {
            "actuator_id": self.actuator_id,
            "state": self.state,
            "timestamp": datetime.now().isoformat(),
        }
        self.client.publish(
            self.topic_state,
            json.dumps(payload),
            qos=QOS_CRITICAL,
            retain=RETAIN_STATE,
        )
        print(f"[{self.actuator_id}] État: {self.state}")

    def start(self) -> None:
        try:
            self.client.connect(BROKER_HOST, BROKER_PORT, BROKER_KEEPALIVE)
            print(f"[{self.actuator_id}] 🚀 Démarré")
            self.client.loop_forever()
        except KeyboardInterrupt:
            print(f"[{self.actuator_id}] 🛑 Arrêt")
        finally:
            self.client.disconnect()
