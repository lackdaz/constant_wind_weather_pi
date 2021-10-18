#!/usr/bin/env python3

# -*- coding: utf-8 -*-
from functools import wraps, lru_cache
import re
import serial
from typing import Optional
import semver

from pydantic import Field
from pydantic.dataclasses import dataclass

DEFAULT_BITDEPTH = 7

ser = serial.Serial(
    port="/dev/ttyAMA1",
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=None,
)


def flush_input_buffer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ser.reset_input_buffer()
        return func(*args, **kwargs)

    return wrapper


def serial_read() -> str:
    byte_array = []
    while True:
        a = ser.read()
        # look for newline
        if int.from_bytes(a, byteorder="big") == 0x0A:
            break
        byte_array += a
    decoded_chars = "".join([chr(byte) for byte in byte_array])
    return decoded_chars


@flush_input_buffer
def get_version():
    # ser.reset_input_buffer()
    ser.write(bytes("01\n", encoding="utf-8"))
    version = re.findall(r"(?<=Ver ).*", serial_read().rstrip())[0]
    assert semver.parse(version)
    return version


@lru_cache(maxsize=128)
def map(x, in_min, in_max, out_min, out_max):
    """maps a value to another interpolated set

    memoisation just because the raspberry pi has too much memory"""
    x = max(x, in_min)  # clamp values
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


@dataclass
class Anemometer:
    """Class for windspeed measurements

    01 -> version
    02 -> get bit depth
    03 -> set bit depth: e.g. "03 07" for 2**7 subsamples
    04 -> set subsampling rate: e.g. "04 05" for 5 hz
    """

    version: Optional[str] = Field(default_factory=get_version)
    bit_depth: Optional[int] = Field(None, ge=2, le=99)
    subsamples: Optional[int] = Field(None, ge=2, le=999)
    sampling_rate: Optional[int] = Field(None, ge=1, le=99)
    subsamples: Optional[int] = Field(None, ge=1, le=99)
    voltage: Optional[float] = Field(None, ge=0.4, le=2.0)
    wind_speed: Optional[float] = Field(None, ge=0.0, le=32.4)
    wind_speed_kmh: Optional[float] = Field(None, ge=0.0, le=116.64)
    wind_speed_kn: Optional[float] = Field(None, ge=0.0, le=62.9856)

    @flush_input_buffer
    def set_subsampling(self, hz: int):
        """faster samples"""
        ser.write(bytes(f"04 {hz:02d}\n", encoding="utf-8"))
        self.sampling_rate = hz
        return self.sampling_rate

    def get_bit_depth(self) -> int:
        """get bit-depth. Higher bit-depth = more accuracy. Refer to class docs"""
        ser.write(bytes("02\n", encoding="utf-8"))
        self.bit_depth = int(serial_read().rstrip())
        return self.bit_depth

    @flush_input_buffer
    def set_bit_depth(self, bit_depth: int = DEFAULT_BITDEPTH) -> int:
        """set bit-depth. Refer to class docs"""
        ser.write(bytes(f"03 {bit_depth:02d}\n", encoding="utf-8"))
        self.bit_depth = self.get_bit_depth()
        self.subsamples = 2 ** bit_depth
        return self.bit_depth

    @flush_input_buffer
    def get_reading(self) -> float:
        """gets subsample buffered reading from the anemometer

        Seth fucked up here because he is hungry"""
        raw_data = serial_read().rstrip()
        # positive lookbehind
        subsample_match = re.match(r"(?:Sample: )(.*)", raw_data)
        if subsample_match:
            # divide by number of subsamples
            analog_value = int(subsample_match.group(1)) / (
                self.subsamples or 2 ** self.set_bit_depth()
            )
            self.voltage = map(analog_value, 0, 1023, 0, 3.3)
            self.wind_speed = map(self.voltage, 0.404, 2.0, 0.0, 32.4)
            self.wind_speed_kmh = self.wind_speed * 3.6  # 3600 / 1000
            self.wind_speed_kn = self.wind_speed_kmh * 1.944  # * 1.852 km/h
        else:
            raise "bad, bad reading"


if __name__ == "__main__":
    print(f"weather_station: v{get_version()}")
    ane = Anemometer()
    import time

    while True:
        ane.get_reading()
        print(ane)
        time.sleep(1)
