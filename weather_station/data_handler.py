import requests
from dataclasses import dataclass, asdict
import logging
import time

try:
    from weather_station.anemometer import Anemometer
    from weather_station.temp_probe import take_spot_reading
except ImportError:
    from anemometer import Anemometer
    from temp_probe import take_spot_reading

URL = "http://gotwind.live/data"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Payload:
    windspeed: float
    temperature: float
    humidity: float

    def post(self):
        try:
            payload = asdict(self)
            res = requests.post(URL, json=payload)
            if res.status_code == 200:
                logger.info(f"posted {payload}")
            else:
                logger.error(f"something went wrong. {res.status_code}")
        except Exception:
            logger.error("something went very wrong")


def poll(sleep: int = 10):
    anemometer = Anemometer()
    while True:
        anemometer.get_reading()
        temp, humidity = take_spot_reading()
        payload = Payload(
            windspeed=anemometer.wind_speed_kn,
            temperature=temp,
            humidity=humidity,
        )
        payload.post()
        time.sleep(sleep)
