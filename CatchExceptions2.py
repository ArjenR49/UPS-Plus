#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ar - 11-05-2021

# import os
import time
# import smbus2
from smbus2 import SMBus

# Define I2C bus
DEVICE_BUS = 1

# Define device I2C slave address.
DEVICE_ADDR = 0x17

# Raspberry Pi Communicates with MCU via I2C protocol.
# bus = smbus2.SMBus(DEVICE_BUS)

# Essential UPS I2C register default values
# (name format: Operation Mode Register Address)
# for shut down & power off state
OMR0x18 = 0    # seconds, power off delay
OMR0x19 = 0    # boolean, automatic restart or not
OMR0x1A = 240  # seconds, power up delay

# Write byte to specified I2C register address
def putByte(RA, byte):
    with SMBus(DEVICE_BUS) as bus:
        bus.write_byte_data(DEVICE_ADDR, RA, byte)

def getByte(RA):
    with SMBus(DEVICE_BUS) as bus:
        byte = bus.read_byte_data(DEVICE_ADDR, RA)
    return [byte]

i = 0
while True:
    try:
        putByte(0x19, 1)
        byte = getByte(0x19)
#        print(i, ' - ', byte)
        putByte(0x19, 0)
        byte = getByte(0x19)
#        print(i, ' - ', byte)
        i += 1
    except TimeoutError as e:
        print(i, ' - ', byte, ' - ', e)
        time.sleep(0.1)
        
# EOF