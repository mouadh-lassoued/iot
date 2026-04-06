import time

from greenhouse.actuators.base_actuator import BaseActuator
from greenhouse.config import TOPICS


class IrrigationActuator(BaseActuator):
    def __init__(self) -> None:
        super().__init__(
            actuator_id="IRRIGATION_01",
            topic_cmd=TOPICS["actuators"]["irrigation"]["cmd"],
            topic_state=TOPICS["actuators"]["irrigation"]["state"],
        )

    def execute_action(self, action: str) -> None:
        if action == "ON":
            print("💧 Irrigation ACTIVÉE")
            print("💧 Arrosage en cours...")
            time.sleep(1)
            print("💧 Eau distribuée aux plantes")
        else:
            print("🛑 Irrigation DÉSACTIVÉE")
            print("🛑 Arrosage arrêté")


if __name__ == "__main__":
    IrrigationActuator().start()
