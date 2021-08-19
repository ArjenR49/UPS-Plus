#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# Enable UPS function "0x1B Reset to Factory Defaults 0/1 Bool"
# ar - 21-05-2021, 07-08-2021, 19-08-2021

from smbus2 import SMBus

DEVICE_BUS = 1
DEVICE_ADDR = 0x17

RESET_FLAG=1

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
        
putByte(0x1B, RESET_FLAG & 0xFF)

print("Register at 0x1B was set to: %d"  % RESET_FLAG)

#EOF
