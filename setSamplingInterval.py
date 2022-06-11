#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# modified from script by @frtz13: ar - 08-06-2021, 11-06-2022

import sys
import smbus2

# Define I2C bus
DEVICE_BUS = 1

# Define device i2c slave address.
DEVICE_ADDR = 0x17

print("-"*60)
print("Modify battery sampling interval for UPS Plus")
print("-"*60)

SI_Min = 1
SI_Max = 1440

# Raspberry Pi communicates with MCU via i2c protocol.
bus = smbus2.SMBus(DEVICE_BUS)
currentSamplingInterval = bus.read_byte_data(DEVICE_ADDR, 0x16) << 0o10 | bus.read_byte_data(DEVICE_ADDR, 0x15)
print("Current value:  %d min" % currentSamplingInterval)

if len(sys.argv) > 1:
    try:
        givenSI = int(sys.argv[1])
        if givenSI >= SI_Min and givenSI <= SI_Max :
            bus.write_byte_data(DEVICE_ADDR, 0x15, givenSI & 0xFF)
            bus.write_byte_data(DEVICE_ADDR, 0x16, (givenSI >> 0o10) & 0xFF)
            print("Successfully changed the battery sampling interval to: %d min" % givenSI)
        else:
            errMsg = "Valid sampling interval values range from {:.0f} to {:.0f} min".format(SI_Min, SI_Max)
            print(errMsg)
    except Exception as exc:
        print("Incorrect parameter: {}. ({})".format(sys.argv[1], str(exc)))
else:
    print("Usage: {} <sampling_interval_in_minutes>".format(sys.argv[0]))
    print("<sampling_interval_in_minutes> between {:.0f} and {:.0f}".format(SI_Min,SI_Max))