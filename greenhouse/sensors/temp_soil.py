import random

from greenhouse.config import SENSOR_INTERVALS, SENSOR_RANGES, TOPICS
from greenhouse.sensors.base_sensor import BaseSensor


class TemperatureSoilSensor(BaseSensor):
    def __init__(self) -> None:
        super().__init__(
            sensor_id="TEMP_SOIL_01",
            topic=TOPICS["sensors"]["temp_soil"],
            interval=SENSOR_INTERVALS["temp_soil"],
        )
        self.min_temp, self.max_temp = SENSOR_RANGES["temp_soil"]

    def read_value(self):
        return round(random.uniform(self.min_temp, self.max_temp), 1)

    def get_unit(self) -> str:
        return "°C"


if __name__ == "__main__":
    TemperatureSoilSensor().start()
