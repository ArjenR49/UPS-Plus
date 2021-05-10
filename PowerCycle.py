#!/usr/bin/python
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 10-05-2021

# ''' Halt the Pi, power down, then power up Pi (= perform power cycle) '''

import os
import time
import smbus2

# Define I2C bus
DEVICE_BUS = 1

# Define device I2C slave address.
DEVICE_ADDR = 0x17

# Essential UPS I2C register default values (name format: Operation Mode Register Address)
# for shut down & power off state
OMR0x18=0   # seconds, power off delay
OMR0x19=0   # boolean, automatic restart (1) or not (0)
OMR0x1A=120  # seconds, power up delay

# Raspberry Pi Communicates with MCU via I2C protocol.
bus = smbus2.SMBus(DEVICE_BUS)

print("*"*62)
print(("*** {:^54s} ***").format("Make the UPS sync & shut down Pi in an orderly manner"))
print(("*** {:^54s} ***").format("without delay & turn power off after "+str(OMR0x1A)+" seconds."))
print(("*** {:^54s} ***").format("Five seconds later the UPS will power up the Pi again."))
print("*"*62)
print()
print()

#exit()

# 1. Disable/enable automatic restart on return of external power.
#    Enable: write 1 to register 0x19
#    Disable: write 0 to register 0x19
while True:
    try:
        bus.write_byte_data(DEVICE_ADDR, 0x19, OMR0x19)
        time.sleep(0.1)
        break
    except TimeoutError:
        continue

# For power cycle operation only 'power up' countdown register (0x1A) must be set.
# UPS will cut power to the Pi 5 seconds before the end of the power up countdown,
# allowing the Pi to sync & halt in an orderly manner,
# and then turn power to the Pi on again at 0 seconds.
while True:
    try:
        bus.write_byte_data(DEVICE_ADDR, 0x1A, OMR0x1A)
        time.sleep(0.1)
        break
    except TimeoutError:
        continue

# Make Pi perform sync and then halt.
os.system("sudo shutdown now")

# Script continues executing, indefinitely as it were (& keeping the lock)
# until it is eventually killed by the Pi shutting down.
while True:
    time.sleep(10)

# Control is now left to the UPS' F/W and MCU ...
# EOF
