#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ar - 18-05-2021

# import os
import time
# import smbus2
from smbus2 import SMBus

# Define I2C bus
DEVICE_BUS = 1

# Define device I2C slave address.
DEVICE_ADDR = 0x17

def settle():
    time.sleep(0.1)

# Write byte to specified I2C register address
def putByte(RA, wbyte):
    try:
        with SMBus(DEVICE_BUS) as pbus:
            pbus.write_byte_data(DEVICE_ADDR, RA, wbyte)
        settle()
        with SMBus(DEVICE_BUS) as gbus:
            rbyte = gbus.read_byte_data(DEVICE_ADDR, RA)
        if rbyte >= max((wbyte - 5),0):
            print("Close enough ", wbyte, rbyte)
        if rbyte <  max((wbyte - 5),0):
            raise ValueError
    except ValueError:
        print("Error writing ", wbyte, rbyte)
        pass
        

while True:
    putByte(0x18, 180)
    settle()
    putByte(0x18,   0)
    time.sleep(0.5)

# EOF