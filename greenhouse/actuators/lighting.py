from greenhouse.actuators.base_actuator import BaseActuator
from greenhouse.config import TOPICS


class LightingActuator(BaseActuator):
    def __init__(self) -> None:
        super().__init__(
            actuator_id="LIGHTING_01",
            topic_cmd=TOPICS["actuators"]["lighting"]["cmd"],
            topic_state=TOPICS["actuators"]["lighting"]["state"],
        )

    def execute_action(self, action: str) -> None:
        if action == "ON":
            print("💡 ÉCLAIRAGE ALLUMÉ")
        else:
            print("🌙 Éclairage éteint")


if __name__ == "__main__":
    LightingActuator().start()
