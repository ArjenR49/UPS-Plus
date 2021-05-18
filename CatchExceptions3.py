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

RA = 0x18

# Raspberry Pi Communicates with MCU via I2C protocol.
# bus = smbus2.SMBus(DEVICE_BUS)

# Write byte to specified I2C register address
# def putByte(RA, byte):
#     with SMBus(DEVICE_BUS) as pbus:
#         pbus.write_byte_data(DEVICE_ADDR, RA, byte)
# 
# def getByte(RA):
#     with SMBus(DEVICE_BUS) as gbus:
#         byte = gbus.read_byte_data(DEVICE_ADDR, RA)
#     return [byte]

i = 0
while True:
    try:
        with SMBus(DEVICE_BUS) as pbus:
            pbus.write_byte_data(DEVICE_ADDR, RA, 180)
        with SMBus(DEVICE_BUS) as gbus:
            byte = gbus.read_byte_data(DEVICE_ADDR, RA)
        if (byte in (180,179)):
            pass
            print('OK            ', i, ' - ', byte)
        else:
            print('read != write ', i, ' - ', byte, "NOT in (180,179)")
        with SMBus(DEVICE_BUS) as pbus:
            pbus.write_byte_data(DEVICE_ADDR, RA, 0)
        with SMBus(DEVICE_BUS) as gbus:
            byte = gbus.read_byte_data(DEVICE_ADDR, RA)
        if (byte == 0):
            pass
            print('OK            ', i, ' - ', byte)
        else:
            print('read != write ', i, ' - ', byte, "!= 0")
        time.sleep(1)
        i += 1
    except TimeoutError as e:
        print(i, ' - ', byte, ' - ', e)
        time.sleep(0.1)
    except KeyboardInterrupt:
        break
    except:
        pass


# EOF