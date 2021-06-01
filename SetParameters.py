#!/usr/bin/python
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 21-05-2021

from smbus2 import SMBus

DEVICE_BUS = 1
DEVICE_ADDR = 0x17

# Set threshold for UPS automatic power-off to prevent
# destroying the batteries by excessive discharge (unit: mV).
# DISCHARGE_LIMIT (a.k.a. protection voltage) will be stored in memory at 0x11-0x12
#DISCHARGE_LIMIT = 2500  # for Sanyo NCR18650GA 3450 mAh Li-Ion batteries
#DISCHARGE_LIMIT = 3700  # default from GeeekPi
DISCHARGE_LIMIT = 3200

# Set the sampling interval, unit: min (usually 2).
# During a few seconds all blue charging level LEDs are off
# and only the batteries deliver power to the Pi
# as sampling of battery characteristics takes place.
SAMPLING_INTERVAL = 2  



# Write byte to specified I2C register address 'until it sticks'.
def putByte(RA, wbyte):
    while True:
        try:
            with SMBus(DEVICE_BUS) as pbus:
                pbus.write_byte_data(DEVICE_ADDR, RA, wbyte)
            with SMBus(DEVICE_BUS) as gbus:
                rbyte = gbus.read_byte_data(DEVICE_ADDR, RA)
            if (wbyte) <= rbyte <= (wbyte):
#                print("OK ", wbyte, rbyte)
                break
            else:
                raise ValueError
        except ValueError:
#            print("Write:", wbyte, "!= Read:", rbyte, " Trying again")
            pass
        
# Store DISCHARGE_LIMIT (a.k.a. protection voltage) in memory at 0x11-0x12
putByte(0x11, DISCHARGE_LIMIT & 0xFF)
putByte(0x12, (DISCHARGE_LIMIT >> 0o10) & 0xFF)

# Store SAMPLING_INTERVAL for battery characteristics sampling in memory at 0x15-0x16
putByte(0x15, SAMPLING_INTERVAL & 0xFF)
putByte(0x16, (SAMPLING_INTERVAL >> 0o10) & 0xFF)

print("Discharge limit was set to: %d mV"  % DISCHARGE_LIMIT)
print("Sampling interval was set to: %d min" % SAMPLING_INTERVAL)

#EOF
