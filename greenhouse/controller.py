"""Contrôleur central IoT pour la serre intelligente (Phase 4 - TP3)."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import paho.mqtt.client as mqtt

from greenhouse.config import (
    BROKER_HOST,
    BROKER_KEEPALIVE,
    BROKER_PORT,
    DAY_END_HOUR,
    DAY_START_HOUR,
    QOS_CRITICAL,
    QOS_DEFAULT,
    THRESHOLDS,
    TOPICS,
)

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "greenhouse.log"


def setup_logging() -> logging.Logger:
    """Configure le logging fichier + console."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("greenhouse.controller")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


class GreenhouseController:
    """Contrôleur central: agrège les capteurs et pilote les actionneurs."""

    def __init__(self) -> None:
        self.logger = setup_logging()

        self.client = mqtt.Client(client_id="greenhouse_controller", protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.reconnect_delay_set(min_delay=1, max_delay=10)

        # Données capteurs les plus récentes
        self.sensor_data: dict[str, float] = {
            "temp_soil": 0.0,
            "humidity": 0.0,
            "light": 0.0,
            "water": 0.0,
        }

        # États connus des actionneurs
        self.actuator_states: dict[str, str] = {
            "irrigation": "UNKNOWN",
            "lighting": "UNKNOWN",
        }

        # Map topic -> clé interne
        self.sensor_topic_map = {
            TOPICS["sensors"]["temp_soil"]: "temp_soil",
            TOPICS["sensors"]["humidity"]: "humidity",
            TOPICS["sensors"]["light"]: "light",
            TOPICS["sensors"]["water"]: "water",
        }

    def on_connect(self, client, userdata, flags, rc) -> None:
        if rc != 0:
            self.logger.error("Connexion au broker échouée (code=%s)", rc)
            return

        self.logger.info("Contrôleur connecté à %s:%s", BROKER_HOST, BROKER_PORT)

        client.subscribe("greenhouse/sensors/#", qos=QOS_DEFAULT)
        client.subscribe("greenhouse/actuators/+/state", qos=QOS_CRITICAL)
        self.logger.info("Abonnements actifs: greenhouse/sensors/#, greenhouse/actuators/+/state")

    def on_disconnect(self, client, userdata, rc) -> None:
        if rc != 0:
            self.logger.warning("Déconnexion inattendue du broker (rc=%s)", rc)

    def on_message(self, client, userdata, msg) -> None:
        topic = msg.topic

        if topic.startswith("greenhouse/sensors/"):
            self.handle_sensor_data(topic, msg.payload)
            return

        if topic.startswith("greenhouse/actuators/") and topic.endswith("/state"):
            self.handle_actuator_state(topic, msg.payload)
            return

    def handle_sensor_data(self, topic: str, payload_raw: bytes) -> None:
        try:
            payload = json.loads(payload_raw.decode())
            value = float(payload["value"])
        except Exception as exc:
            self.logger.warning("Payload capteur invalide sur %s: %s", topic, exc)
            return

        sensor_key = self.sensor_topic_map.get(topic)
        if sensor_key is None:
            self.logger.warning("Topic capteur non reconnu: %s", topic)
            return

        self.sensor_data[sensor_key] = value
        self.logger.info("Capteur %s = %s", sensor_key, value)
        self.apply_rules()

    def apply_rules(self) -> None:
        self._rule_irrigation()
        self._rule_lighting()
        self._rule_temp_alert()

    def _rule_irrigation(self) -> None:
        humidity = self.sensor_data["humidity"]
        water = self.sensor_data["water"]

        should_on = humidity < THRESHOLDS["humidity_low"] and water > THRESHOLDS["water_min"]
        target_state = "ON" if should_on else "OFF"

        reason = (
            f"humidity={humidity:.1f}% (<{THRESHOLDS['humidity_low']}) and "
            f"water={water:.1f}% (>{THRESHOLDS['water_min']})"
            if should_on
            else f"humidity={humidity:.1f}%, water={water:.1f}%"
        )
        self.send_command("irrigation", target_state, reason=reason)

    def _rule_lighting(self) -> None:
        light = self.sensor_data["light"]
        hour = datetime.now().hour

        in_day_window = DAY_START_HOUR <= hour < DAY_END_HOUR
        should_on = light < THRESHOLDS["light_low"] and in_day_window
        target_state = "ON" if should_on else "OFF"

        reason = (
            f"light={light:.1f}lux (<{THRESHOLDS['light_low']}) and hour={hour}"
            if should_on
            else f"light={light:.1f}lux, hour={hour}, plage={DAY_START_HOUR}-{DAY_END_HOUR}"
        )
        self.send_command("lighting", target_state, reason=reason)

    def _rule_temp_alert(self) -> None:
        temp = self.sensor_data["temp_soil"]
        if temp <= THRESHOLDS["temp_critical"]:
            return

        alert_payload = {
            "level": "CRITICAL",
            "type": "TEMP_SOIL",
            "message": (
                f"Température sol critique: {temp:.1f}°C "
                f"(seuil {THRESHOLDS['temp_critical']}°C)"
            ),
            "value": temp,
            "threshold": THRESHOLDS["temp_critical"],
            "timestamp": datetime.now().isoformat(),
        }
        self.client.publish(TOPICS["alerts"], json.dumps(alert_payload), qos=QOS_CRITICAL)
        self.logger.critical("ALERTE CRITIQUE publiée: %s", alert_payload["message"])

    def handle_actuator_state(self, topic: str, payload_raw: bytes) -> None:
        """Met à jour l'état interne selon les retours des actionneurs."""
        try:
            payload = json.loads(payload_raw.decode())
            state = str(payload.get("state", "UNKNOWN")).upper()
        except Exception as exc:
            self.logger.warning("Payload état actionneur invalide (%s): %s", topic, exc)
            return

        parts = topic.split("/")
        # greenhouse/actuators/<name>/state
        if len(parts) < 4:
            self.logger.warning("Topic état actionneur invalide: %s", topic)
            return

        actuator_key = parts[2]
        self.actuator_states[actuator_key] = state
        self.logger.info("État actionneur %s = %s", actuator_key, state)

    def send_command(self, actuator_key: str, action: str, reason: str = "") -> None:
        """Envoie commande JSON QoS 1 à un actionneur (si changement d'état)."""
        current_state = self.actuator_states.get(actuator_key)
        if current_state == action:
            return

        topic_cmd = TOPICS["actuators"][actuator_key]["cmd"]
        payload: dict[str, Any] = {
            "action": action,
            "source": "controller",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }

        self.client.publish(topic_cmd, json.dumps(payload), qos=QOS_CRITICAL)
        self.actuator_states[actuator_key] = action
        self.logger.info("Commande envoyée -> %s: %s (%s)", actuator_key, action, reason)

    def start(self) -> None:
        self.logger.info("Démarrage contrôleur central...")
        self.client.connect(BROKER_HOST, BROKER_PORT, BROKER_KEEPALIVE)
        self.client.loop_forever()


if __name__ == "__main__":
    GreenhouseController().start()
