import random

from greenhouse.config import SENSOR_INTERVALS, SENSOR_RANGES, TOPICS
from greenhouse.sensors.base_sensor import BaseSensor


class HumiditySensor(BaseSensor):
    def __init__(self) -> None:
        super().__init__(
            sensor_id="HUMIDITY_01",
            topic=TOPICS["sensors"]["humidity"],
            interval=SENSOR_INTERVALS["humidity"],
        )
        self.min_humidity, self.max_humidity = SENSOR_RANGES["humidity"]

    def read_value(self):
        return round(random.uniform(self.min_humidity, self.max_humidity), 1)

    def get_unit(self) -> str:
        return "%"


if __name__ == "__main__":
    HumiditySensor().start()
