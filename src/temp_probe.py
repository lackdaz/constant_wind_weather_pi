#!/usr/bin/env python3

import board
import busio
from adafruit_am2320 import AM2320
from time import sleep
from pydantic.dataclasses import dataclass

READOUT_BACKOFF = 0.1


@dataclass
class TempProbe:
    pass


def take_spot_reading():
    try:
        with busio.I2C(board.SCL, board.SDA) as i2c:
            sensor = AM2320(i2c)
            temp = take_spot_temp(sensor)
            humidity = take_spot_rel_humidity(sensor)
            return temp, humidity
    except RuntimeError as err:
        if str(err) == "I2C read failure":
            return take_spot_reading()


def take_spot_temp(probe) -> float:
    tries = 0
    while True:
        try:
            temp = probe.temperature
            break
        except OSError:
            tries += 1
            sleep(READOUT_BACKOFF)
    return temp


def take_spot_rel_humidity(probe) -> float:
    tries = 0
    while True:
        try:
            rel_humd = probe.relative_humidity
            break
        except OSError:
            tries += 1
            sleep(READOUT_BACKOFF)
    return rel_humd


if __name__ == "__main__":
    while True:
        temp, humidity = take_spot_reading()
        print(f"temp is {temp}°C, humidity is {humidity}%")
        sleep(0.5)
