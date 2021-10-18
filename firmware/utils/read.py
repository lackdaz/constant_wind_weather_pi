#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import serial
import re
from functools import lru_cache

# print(serial.__version__)
ser = serial.Serial(
    port="/dev/ttyAMA1",
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=None,
)


byte_array = []
decoded_stripped: int = -1
bit_depth = 7
subsamples = 2 ** bit_depth


@lru_cache(maxsize=128)
def map(x, in_min, in_max, out_min, out_max):
    x = max(x, in_min)  # clamp values
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


while True:
    while True:
        a = ser.read()
        # look for newline
        if int.from_bytes(a, byteorder="big") == 0x0A:
            break
        byte_array += a
    decoded = "".join([chr(byte) for byte in byte_array])
    sample = re.match("Sample:", decoded)
    if sample:
        decoded_stripped: int = int(decoded.replace("Sample: ", ""))
        analog_value = decoded_stripped / (subsamples)
        voltage = map(analog_value, 0, 1023, 0, 3.3)
        wind_speed = map(voltage, 0.404, 2.0, 0.0, 32.4)
        wind_speed_kmh = wind_speed * 3.6  # 3600 / 1000
        wind_speed_knot = wind_speed * 1.944  # 1.852 km/h

    print(
        f"voltage: {voltage:.4f}V, wind_speed: {wind_speed_kmh:.2f}km/h or {wind_speed_knot:.2f}kn"
    )
    print("---")
    byte_array = []
