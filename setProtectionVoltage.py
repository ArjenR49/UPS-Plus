#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# modified from script by @frtz13: ar - 08-06-2021

import sys
import smbus2

# Define I2C bus
DEVICE_BUS = 1

# Define device i2c slave address.
DEVICE_ADDR = 0x17

print("-"*60)
print("Modify battery protection voltage for UPS Plus")
print("-"*60)

PV_Mini_mV = 2500
PV_Maxi_mV = 4000

# Raspberry Pi communicates with MCU via i2c protocol.
bus = smbus2.SMBus(DEVICE_BUS)
currentProtectionVoltage_mV = bus.read_byte_data(DEVICE_ADDR, 0x12) << 0o10 | bus.read_byte_data(DEVICE_ADDR, 0x11)
print("Current value:  %d mV" % currentProtectionVoltage_mV)

if len(sys.argv) > 1:
    try:
        givenPV_mV = int(sys.argv[1])
        if givenPV_mV >= PV_Mini_mV and givenPV_mV <= PV_Maxi_mV :
            bus.write_byte_data(DEVICE_ADDR, 0x11, givenPV_mV & 0xFF)
            bus.write_byte_data(DEVICE_ADDR, 0x12, (givenPV_mV >> 0o10) & 0xFF)
            print("Successfully set the protection voltage to: %d mV" % givenPV_mV)
        else:
            errMsg = "Valid protection voltage values range from {:.0f} to {:.0f} mV".format(PV_Mini_mV, PV_Maxi_mV)
            print(errMsg)
    except Exception as exc:
        print("Incorrect parameter: {}. ({})".format(sys.argv[1], str(exc)))
else:
    print("Usage: {} <protection_voltage_in_mV>".format(sys.argv[0]))
    print("<protection_voltage_in_mV> between {:.0f} and {:.0f}".format(PV_Mini_mV,PV_Maxi_mV))