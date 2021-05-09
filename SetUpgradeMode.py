#!/usr/bin/python
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 08-05-2021

# How to enter OTA mode:
#
# After setting (=running this script):
# python3 $HOME/UPS+/SetUpgradeMode.py
# shut down the Pi,
# unplug the external power supply,
# remove the batteries,
# reinsert the batteries,

# MAKING DOUBLE SURE THE BATTERIES GO IN THE RIGHT WAY
# MAKING DOUBLE SURE THE BATTERIES GO IN THE RIGHT WAY

# Optionally reconnect the external power supply.

# Run the upgrade program:
# python3 $HOME/UPS+/OTA_firmware_upgrade.py

# This downloads & upgrades the firmware. 
# When the upgrade program is finished,
# it will shutdown your Raspberry Pi automatically,
# and you need to disconnect the charger and remove all batteries from UPS
# and then insert the batteries again,

# MAKING DOUBLE SURE THE BATTERIES GO IN THE RIGHT WAY
# MAKING DOUBLE SURE THE BATTERIES GO IN THE RIGHT WAY

# Now press the function button to turn on the UPS.

# --------------------------------------------------------------------------
import smbus2

DEVICE_BUS = 1
DEVICE_ADDR = 0x17

bus = smbus2.SMBus(DEVICE_BUS)

# Set OTA mode
#bus.write_byte_data(DEVICE_ADDR, 50, 127)
while True:
    try:
        bus.write_byte_data(DEVICE_ADDR, 0x32, 0x7F)
        break
    except TimeoutError:
        continue

#EOF