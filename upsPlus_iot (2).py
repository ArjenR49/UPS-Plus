#!/usr/bin/python
# -*- coding: utf-8 -*-

# modified by ar - 08-05-2021

# ''' Update the status of batteries to IoT platform '''

import os
import time
import smbus2
import requests
from ina219 import INA219,DeviceRangeError
import random
from datetime import datetime, timezone

DEVICE_BUS = 1
DEVICE_ADDR = 0x17
#PROTECT_VOLT = 3700
SAMPLE_TIME = 2
FEED_URL = "https://api.thekoziolfoundation.com/feed"
#time.sleep(random.randint(0, 59))

DATA = dict()

ina = INA219(0.00725, address=0x40)
ina.configure()
DATA['PiVccVolt'] = ina.voltage()
DATA['PiIddAmps'] = ina.current()

ina = INA219(0.005, address=0x45)
ina.configure()
DATA['BatVccVolt'] = ina.voltage()
try:
    DATA['BatIddAmps'] = ina.current()
except DeviceRangeError:
    DATA['BatIddAmps'] = 16000

bus = smbus2.SMBus(DEVICE_BUS)

aReceiveBuf = []
aReceiveBuf.append(0x00)

i=0x01
while i<0x100:
    try:
        aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
        i=i+1
        time.sleep(0.1)
    except TimeoutError:
        continue

#for i in range(0x01, 0xFF):
#    aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))

DATA['McuVccVolt']      = aReceiveBuf[0x02] << 0o10 | aReceiveBuf[0x01]
DATA['BatPinCVolt']     = aReceiveBuf[0x06] << 0o10 | aReceiveBuf[0x05]
DATA['ChargeTypeCVolt'] = aReceiveBuf[0x08] << 0o10 | aReceiveBuf[0x07]
DATA['ChargeMicroVolt'] = aReceiveBuf[0x0A] << 0o10 | aReceiveBuf[0x09]

DATA['BatTemperature']  = aReceiveBuf[0x0C] << 0o10 | aReceiveBuf[0x0B]
DATA['BatFullVolt']     = aReceiveBuf[0x0E] << 0o10 | aReceiveBuf[0x0D]
DATA['BatEmptyVolt']    = aReceiveBuf[0x10] << 0o10 | aReceiveBuf[0x0F]
DATA['BatProtectVolt']  = aReceiveBuf[0x12] << 0o10 | aReceiveBuf[0x11]
DATA['SampleTime']      = aReceiveBuf[0x16] << 0o10 | aReceiveBuf[0x15]
DATA['AutoPowerOn']     = aReceiveBuf[0x19]

DATA['OnlineTime']      = aReceiveBuf[0x1F] << 0o30 | aReceiveBuf[0x1E] << 0o20 | aReceiveBuf[0x1D] << 0o10 | aReceiveBuf[0x1C]
DATA['FullTime']        = aReceiveBuf[0x23] << 0o30 | aReceiveBuf[0x22] << 0o20 | aReceiveBuf[0x21] << 0o10 | aReceiveBuf[0x20]
DATA['OneshotTime']     = aReceiveBuf[0x27] << 0o30 | aReceiveBuf[0x26] << 0o20 | aReceiveBuf[0x25] << 0o10 | aReceiveBuf[0x24]
DATA['Version']         = aReceiveBuf[0x29] << 0o10 | aReceiveBuf[0x28]

DATA['UID0'] = "%08X" % (aReceiveBuf[0xF3] << 0o30 | aReceiveBuf[0xF2] << 0o20 | aReceiveBuf[0xF1] << 0o10 | aReceiveBuf[0xF0])
DATA['UID1'] = "%08X" % (aReceiveBuf[0xF7] << 0o30 | aReceiveBuf[0xF6] << 0o20 | aReceiveBuf[0xF5] << 0o10 | aReceiveBuf[0xF4])
DATA['UID2'] = "%08X" % (aReceiveBuf[0xFB] << 0o30 | aReceiveBuf[0xFA] << 0o20 | aReceiveBuf[0xF9] << 0o10 | aReceiveBuf[0xF8])

#time.sleep(random.randint(0, 59))

# Record starting time of upload
StartTime = datetime.now(timezone.utc).astimezone()
TimeStampA = '{:%d-%m-%Y %H:%M:%S}'.format(StartTime)
print(("START - UPS data upload to Koziol Foundation: {:<s}").format(TimeStampA))
print(DATA)
r = requests.post(FEED_URL, data=DATA)
print(r.text)
print('END\n')

#EOF