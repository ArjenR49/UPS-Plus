#!/usr/bin/python
# -*- coding: utf-8 -*-

# Slightly edited from GeeekPi original script
# ar - 16-05-2021

import os
import time
import json
import smbus2
import requests

# How to enter into OTA mode:
#
# Method 1) Setting register in terminal: i2cset -y 1 0x17 50 127 b
# (can be done in terminal by running: python3 SetUpgradeMode.py)
#
# Method 2) Remove all power connections and batteries, and then hold the power button, insert the batteries.

# Define device bus and address, and firmware url.
DEVICE_BUS = 1
DEVICE_ADDR = 0x18 # OTA Firmware Upgrade Mode
UPDATE_URL = "https://api.thekoziolfoundation.com/update"

# Instance of bus.
bus = smbus2.SMBus(DEVICE_BUS)
aReceiveBuf = []

for i in range(0xF0, 0xFC):
    aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))

UID0 = "%08X" % (aReceiveBuf[0x03] << 0o30 | aReceiveBuf[0x02] << 0o20 | aReceiveBuf[0x01] << 0o10 | aReceiveBuf[0x00])
UID1 = "%08X" % (aReceiveBuf[0x07] << 0o30 | aReceiveBuf[0x06] << 0o20 | aReceiveBuf[0x05] << 0o10 | aReceiveBuf[0x04])
UID2 = "%08X" % (aReceiveBuf[0x0B] << 0o30 | aReceiveBuf[0x0A] << 0o20 | aReceiveBuf[0x09] << 0o10 | aReceiveBuf[0x08])

r = requests.post(UPDATE_URL, data={"UID0":UID0, "UID1":UID1, "UID2":UID2})
r = json.loads(r.text)

if r['code'] != 0:
    print('Could not get the firmware due to:' + r['reason'])
    exit(r['code'])
else:
    print('Passed authentication, now downloading the latest firmware ...')
    req = requests.get(r['url'])
    with open("/tmp/firmware.bin", "wb") as f:
        f.write(req.content)
    print("Firmware downloaded successfully.")
    
    print("Please keep the UPS+ powered, while the firmware is being upgraded.")
    print("Disconnecting power during the upgrade will cause unrecoverable failure of the UPS!")
    with open("/tmp/firmware.bin", "rb") as f:
        while True:
            data = f.read(0x10)
            for i in range(len(list(data))):
                bus.write_byte_data(0x18, i + 1, data[i])
            bus.write_byte_data(0x18, 0x32, 0xFA)
            time.sleep(0.1)
            print('.', end='',flush=True)

            if len(list(data)) == 0:
                bus.write_byte_data(0X18, 0x32, 0x00)
                print('.', flush=True)
                print('Firmware upgrade completed.')
                print('Please disconnect all power/batteries and reinsert to start using the new firmware.')
                os.system("sudo halt")
                while True:
                    time.sleep(10)
#EOF