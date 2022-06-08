#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 08-05-2021, 30-05-2022, 03-06-2022, 09-06-2022

# ''' Halt the Pi, cut power, then restore power a few minutes later, so Pi starts up again (= perform power cycle) '''

import os
import sys
import time
import smbus2
import click

# Define I2C bus
DEVICE_BUS = 1

# Define device I2C slave address.
DEVICE_ADDR = 0x17

# UPS I2C registers used in this script (name format: Operation Mode Register Address)
# Set only one of 0x18 or 0x19 unequal to 0, not both!
# The values given here determine how the UPS+ will proceed after this script ends.
OMR0x18=0   # seconds, power off delay, power stays off
OMR0x19=0   # boolean, automatic restart or not upon return of external power
OMR0x1A=60  # seconds, power off delay with subsequent restoring power about 10 minutes later.

# Raspberry Pi Communicates with MCU via I2C protocol.
bus = smbus2.SMBus(DEVICE_BUS)

print("*"*62)
print(("*** {:^54s} ***").format("-- Perform a controlled power cycle --"))
print(("*** {:^54s} ***").format("Script shuts down OS in an orderly manner and makes"))
print(("*** {:^54s} ***").format("the UPS+ cut power to the Pi after "+str(OMR0x1A)+" seconds."))
print(("*** {:^54s} ***").format("About 8 minutes later the UPS+ restores power,"))
print(("*** {:^54s} ***").format("and the Pi will start up again."))
print("*"*62)
print()

if len(sys.argv) == 1:
    if click.confirm('Do you want to continue?', default=True):
        click.echo('Initiating power cycle ...')
    else:
        print('Script aborted')
        exit()
elif (len(sys.argv) > 1) and not (sys.argv[1]=="yes"):
    print("Incorrect parameter")
    print("Syntax for non-interactive use is: PowerCycle.py yes")
    exit()
    
print('Initiating power cycle ...')

#exit()

# Set UPS power down timer (unit: seconds) to allow the Pi ample time to sync & shutdown.
# For power down without restart only 'power down' countdown register (0x18) must be set.
while True:
    try:
        bus.write_byte_data(DEVICE_ADDR, 0x18, OMR0x18)
        time.sleep(0.1)
        break
    except TimeoutError:
        continue


# Automatic restart on return of external power?
# Used in the UPS+ control script.
#    Enable:  write 1 to register 0x19
#    Disable: write 0 to register 0x19
while True:
    try:
        bus.write_byte_data(DEVICE_ADDR, 0x19, OMR0x19)
        time.sleep(0.1)
        break
    except TimeoutError:
        continue

# For power cycling only the 'restart countdown' register (0x1A) must be set!
# The UPS+ will disconnect power from the Pi at the end of the countdown,
# thus allowing the script to make the OS shut down before the power is cut.
# About 8 minutes later the UPS+ restores power to the Pi, which will then restart.
while True:
    try:
        bus.write_byte_data(DEVICE_ADDR, 0x1A, OMR0x1A)
        time.sleep(0.1)
        break
    except TimeoutError:
        continue

# Make Pi perform sync and then halt.
os.system("sudo sync && sudo halt &")

# Script continues executing, indefinitely as it were (& keeping the lock)
# until it is eventually killed by the Pi shutting down.
while True:
    time.sleep(10)

# Control is now left to the UPS' F/W and MCU ...
# EOF
