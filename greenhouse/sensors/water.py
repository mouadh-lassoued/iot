import random

from greenhouse.config import SENSOR_INTERVALS, SENSOR_RANGES, TOPICS
from greenhouse.sensors.base_sensor import BaseSensor


class WaterLevelSensor(BaseSensor):
    def __init__(self) -> None:
        super().__init__(
            sensor_id="WATER_01",
            topic=TOPICS["sensors"]["water"],
            interval=SENSOR_INTERVALS["water"],
        )
        self.min_water, self.max_water = SENSOR_RANGES["water"]

    def read_value(self):
        return round(random.uniform(self.min_water, self.max_water), 1)

    def get_unit(self) -> str:
        return "%"


if __name__ == "__main__":
    WaterLevelSensor().start()
