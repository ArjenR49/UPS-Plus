#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 13-05-2021

# ''' Halt the Pi, power down, then power up Pi (= perform power cycle) '''

import os
import time
from smbus2 import SMBus 

# Define I2C bus
DEVICE_BUS = 1

# Define device I2C slave address.
DEVICE_ADDR = 0x17

# Essential UPS I2C register default values
# (name format: Operation Mode Register Address)
# for shut down & power off state
OMR0x18 = 0   # seconds, power off delay
OMR0x19 = 0   # boolean, automatic restart or not
OMR0x1A = 75  # seconds, power on delay

# Write byte to specified I2C register address
def putByte(RA, byte):
    while True:
        try:
            with SMBus(DEVICE_BUS) as bus:
                bus.write_byte_data(DEVICE_ADDR, RA, byte)
                break
        except TimeoutError:
            time.sleep(0.1)

print("*"*62)
print(("*** {:^54s} ***").
      format("Make the UPS sync & shut down Pi in an orderly manner"))
print(("*** {:^54s} ***").format("without delay & turn power off after "
      + str(OMR0x1A)+" seconds."))
print(("*** {:^54s} ***").
      format("Five seconds later the UPS will power up the Pi again."))
print("*"*62)
print()
print()

# Disable/enable automatic restart on return of external power.
#   Enable: write 1 to register 0x19
#   Disable: write 0 to register 0x19
putByte(0x19, OMR0x19)
time.sleep(2)

# For power cycle operation only 'power up' countdown (0x1A) must be set.
# UPS will cut power to the Pi 5 seconds before the end of the power up
# countdown, allowing the Pi to sync & halt in an orderly manner,
# and then turn power to the Pi on again at 0 seconds.
putByte(0x1A, OMR0x1A)
time.sleep(2)

# Halt the Pi without delay.
os.system("sudo shutdown now")

# Script continues executing, indefinitely as it were (& keeping the lock)
# until it is eventually killed by the Pi shutting down.
while True:
    time.sleep(10)

# Control is now left to the UPS' F/W and MCU ...
# EOF
