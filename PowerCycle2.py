#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 19-05-2021

# ''' Halt the Pi, power down, then power up Pi (= perform power cycle) '''

import os
import time
from smbus2 import SMBus 

# Define I2C bus
DEVICE_BUS = 1

# Define device I2C slave address.
DEVICE_ADDR = 0x17

# Essential UPS I2C power control registers
# (name format: Operation Mode Register Address)
# Default values for shut down & power off state
OMR0x18S = 0   # seconds, power off delay (no restart)
OMR0x19S = 0   # boolean, automatic restart (1) or not (0) upon return of external power
OMR0x1AS = 60  # seconds, power off timer (with automatic restart ca. 10 min. later)

# Write byte to specified I2C register address 'until it sticks'.
def putByte(RA, wbyte):
    while True:
        try:
            with SMBus(DEVICE_BUS) as pbus:
                pbus.write_byte_data(DEVICE_ADDR, RA, wbyte)
            with SMBus(DEVICE_BUS) as gbus:
                rbyte = gbus.read_byte_data(DEVICE_ADDR, RA)
            if (wbyte) <= rbyte <= (wbyte):
                print("OK ", wbyte, rbyte)
                break
            else:
                raise ValueError
        except ValueError:
            print("Write:", wbyte, "!= Read:", rbyte, " Trying again")
            pass
        
print("*"*62)
print(("*** {:^54s} ***").
      format("Have the UPS shut down the Pi in an orderly manner"))
print(("*** {:^54s} ***").format("without delay & turn power off after ca. "
      + str(OMR0x1AS) +" seconds."))
print(("*** {:^54s} ***").
      format("Ca. 10 min later the UPS will power up the Pi again."))
print("*"*62)
print()

# Unset = stop power timers.
putByte(0x18, 0)
putByte(0x1A, 0)

# If only the 'power down' countdown (0x18) is set,
# UPS will cut power to the Pi at or near the end of the countdown,
# allowing the Pi to sync & halt in an orderly manner.
# The Pi will need to be started manually by pressing the UPS button.
putByte(0x18, OMR0x18S)

# Disable/enable automatic restart on return of external power.
#   Enable: write 1 to register 0x19
#   Disable: write 0 to register 0x19
putByte(0x19, OMR0x19S)

# If only the 'power up' countdown (0x1A) is set,
# UPS will cut power to the Pi at or near the end of the countdown,
# allowing the Pi to sync & halt in an orderly manner.
# The UPS will power on the Pi again after ca. 10 min.
putByte(0x1A, OMR0x1AS)

# For test purposes, i.e. dry run 
#exit()

# Halt the Pi without delay.
os.system("sudo shutdown now")

# Script continues executing, indefinitely as it were (& keeping the lock)
# until it is killed by the Pi shutting down.
while True:
    time.sleep(10)

# Control now passes to the UPS' F/W and MCU ...
# EOF