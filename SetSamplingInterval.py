#!/usr/bin/python
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 16-05-2021

import smbus2

DEVICE_BUS = 1
DEVICE_ADDR = 0x17

# Set the sampling interval, unit: min (usually 2).
# During a few seconds all blue charging level LEDs are off
# and only the batteries deliver power to the Pi
# as sampling of battery characteristics takes place.
SAMPLING_INTERVAL = 2  

# Raspberry Pi communicates with MCU via I2C protocol.
bus = smbus2.SMBus(DEVICE_BUS)

while True:
    try:
        bus.write_byte_data(DEVICE_ADDR, 0x15, SAMPLING_INTERVAL & 0xFF)
        bus.write_byte_data(DEVICE_ADDR, 0x16, (SAMPLING_INTERVAL >> 0o10) & 0xFF)
        break
    except TimeoutError:
        continue

print("Sampling interval has been set to: %d Min" % SAMPLING_INTERVAL)
#EOF
