#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ar - 11-05-2021

# import os
import time
import smbus2

# Define I2C bus
DEVICE_BUS = 1

# Define device I2C slave address.
DEVICE_ADDR = 0x17

# Raspberry Pi Communicates with MCU via I2C protocol.
bus = smbus2.SMBus(DEVICE_BUS)

# Essential UPS I2C register default values
# (name format: Operation Mode Register Address)
# for shut down & power off state
OMR0x18 = 0    # seconds, power off delay
OMR0x19 = 0    # boolean, automatic restart or not
OMR0x1A = 240  # seconds, power up delay

# Write byte to specified I2C register address
def putByte(RA, byte):
            bus.write_byte_data(DEVICE_ADDR, RA, byte)

def getByte(RA):
            byte = bus.read_byte_data(DEVICE_ADDR, RA)
            return [byte]

i = 0
while True:
    try:
        putByte(0x19, 1)
        time.sleep(0.1)
        byte = getByte(0x19)
        time.sleep(0.1)
        i += 1
        print(i, ' - ', byte)
        putByte(0x19, 0)
        time.sleep(0.1)
        byte = getByte(0x19)
        time.sleep(0.1)
        i += 1
        print(i, ' - ', byte)
    except Exception as e:
        print(i, ' - ', byte, ' - ', e)
        break

# EOF