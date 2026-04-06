import random

from greenhouse.config import SENSOR_INTERVALS, SENSOR_RANGES, TOPICS
from greenhouse.sensors.base_sensor import BaseSensor


class LightSensor(BaseSensor):
    def __init__(self) -> None:
        super().__init__(
            sensor_id="LIGHT_01",
            topic=TOPICS["sensors"]["light"],
            interval=SENSOR_INTERVALS["light"],
        )
        self.min_light, self.max_light = SENSOR_RANGES["light"]

    def read_value(self):
        return random.randint(self.min_light, self.max_light)

    def get_unit(self) -> str:
        return "lux"


if __name__ == "__main__":
    LightSensor().start()
