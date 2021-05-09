#!/usr/bin/python
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 09-05-2021

import os
import time
import sys
import smbus2
from datetime import datetime, timezone
from math import log10, floor
from ina219 import INA219,DeviceRangeError

#import logging
#import locale
#locale.setlocale(locale.LC_ALL, 'nl_NL')

# Record starting time & format in two styles
StartTime = datetime.now(timezone.utc).astimezone()
TimeStampA = '{:%d-%m-%Y %H:%M:%S}'.format(StartTime)
TimeStampB = '{:%Y-%m-%d_%H:%M:%S}'.format(StartTime)

def round_sig(x, n=3):
    if not x: return 0
    power = -floor(log10(abs(x))) + (n - 1)
    factor = (10 ** power)
    return round(x * factor) / factor

DEVICE_BUS = 1
DEVICE_ADDR = 0x17
SAMPLE_TIME = 2

ina = INA219(0.00725,address=0x40)
ina.configure()
print("Raspberry Pi supply voltage:                      %8.3f V" % round_sig(ina.voltage(),n=3))
print("Raspberry Pi current consumption:                 %8.3f A" % round_sig(ina.current()/1000,n=3))
print("Raspberry Pi power consumption:                   %8.3f W" % round_sig(ina.power()/1000,n=3))

print()
ina = INA219(0.005,address=0x45)
ina.configure()
print(        "Battery voltage (from INA219):                    %8.3f V" % round_sig(ina.voltage(),n=3))
try:
    if ina.current() > 0:
        print("Battery current (charging):                       %8.3f A" % round_sig(abs(ina.current()/1000),n=3))
        print("Power supplied to the batteries:                  %8.3f W" % round_sig(ina.power()/1000,n=3))
    else:
        print("Battery current (discharging):                    %8.3f A" % round_sig(abs(ina.current()/1000),n=2))
        print("Battery power consumption:                        %8.3f W" % round_sig(ina.power()/1000,n=3))
except DeviceRangeError:
    print('Out of Range Warning: BATTERY VOLTAGE EXCEEDING SAFE LIMITS!')
print()

bus = smbus2.SMBus(DEVICE_BUS)

# Path for parameter files
PATH = str(os.getenv('HOME'))+'/UPS+/'

f = open(PATH+'UPS_parameters.txt','rt')
line = f.readline()
POWEROFF_LIMIT = line.strip()
#line = f.readline()
#POWERLOSS_TIMER = line.strip()
f.close()

f = open(PATH+'ExtPowerLost.txt','r')
GRACE_TIME = int(f.read())
f.close()

# Force restart (simulate power plug, write the corresponding number of seconds,
# shut down 5 seconds before the end of the countdown, and then turn on at 0 seconds.)
# bus.write_byte_data(DEVICE_ADDR, 0x1A, 0x1E)

# Restore factory settings
# (clear memory, clear learning parameters, can not clear the cumulative running time, used for after-sales purposes.)
# bus.write_byte_data(DEVICE_ADDR, 0x1B, 0x01)

aReceiveBuf = []
aReceiveBuf.append(0x00)

i=1
while i<0x100:
    try:
        aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
        i=i+1
    except TimeoutError:
        time.sleep(0.1)

print("UPS board MCU voltage:                            %8.3f V" % round_sig((aReceiveBuf[0x02] << 0o10 | aReceiveBuf[0x01])/1000,n=3))
print("Voltage at Pi GPIO header pins:                   %8.3f V" % round_sig((aReceiveBuf[0x04] << 0o10 | aReceiveBuf[0x03])/1000,n=3))

print("USB type C port input voltage:                    %8.3f V" % round_sig((aReceiveBuf[0x08] << 0o10 | aReceiveBuf[0x07])/1000,n=3))
print("Micro USB port input voltage:                     %8.3f V" % round_sig((aReceiveBuf[0x0A] << 0o10 | aReceiveBuf[0x09])/1000,n=3))

# Learned from the battery internal resistance change, the longer the use, the more stable the data:
print("Battery temperature (estimate):                   %8.d°C"  % round_sig(aReceiveBuf[0x0C] << 0o10 | aReceiveBuf[0x0B]))

print()
# Fully charged voltage is learned through charging and discharging:
print("Batteries fully charged at (learned value):       %8.3f V" % round_sig((aReceiveBuf[0x0E] << 0o10 | aReceiveBuf[0x0D])/1000,n=3))

# This value is inaccurate during charging:
print("Current voltage at battery terminals:             %8.3f V" % round_sig((aReceiveBuf[0x06] << 0o10 | aReceiveBuf[0x05])/1000,n=3))

# Voltage below which UPS shuts down the Pi & powers off to conserve battery capacity
print("UPS power-off voltage limit is set at:            %8.3f V" % round_sig(float(POWEROFF_LIMIT)/1000,n=3))

# Fully discharged voltage is learned through charging and discharging:
print("Batteries fully discharged at (learned value):    %8.3f V" % round_sig((aReceiveBuf[0x10] << 0o10 | aReceiveBuf[0x0F])/1000,n=3))

# The deep discharge limit value can be set:
DISCHARGE_LIMIT=(aReceiveBuf[0x12] << 0o10 | aReceiveBuf[0x11])/1000
print("Battery deep discharge limit is set at:           %8.3f V" % round_sig(DISCHARGE_LIMIT,n=3))

# At least one complete charge and discharge cycle needs to pass before this value is meaningful:
print("Remaining battery capacity:                       %8.d %%" % (aReceiveBuf[0x14] << 0o10 | aReceiveBuf[0x13]))

print("Sampling interval:                                %8.d min" % (aReceiveBuf[0x16] << 0o10 | aReceiveBuf[0x15]))

print()
if aReceiveBuf[0x17] == 1:
    print("Current power state: normal")
else:
    print("Current power state: other")

print()
if (aReceiveBuf[0x08] << 0o10 | aReceiveBuf[0x07]) > 4000:
    print('Charging via USB type C connector\n')
    print(("{:<60s}").format("Should the external power be interrupted long enough"))
    print(("{:<60s}").format("to cause the battery voltage to drop below "+str(max(DISCHARGE_LIMIT,round_sig(float(POWEROFF_LIMIT)/1000,n=3)))+" V, or"))
    print(("{:<60s}").format("remain interrupted for more than "+str(GRACE_TIME)+" min,"))
    print(("{:<60s}").format("the Pi will be halted & the UPS will power it down.\n"))
elif (aReceiveBuf[0x0A] << 0o10 | aReceiveBuf[0x09]) > 4000:
    print('Charging via micro USB connector\n')
    print(("{:<60s}").format("Should the external power be interrupted long enough"))
    print(("{:<60s}").format("to cause the battery voltage to drop below "+str(max(DISCHARGE_LIMIT,round_sig(float(POWEROFF_LIMIT)/1000,n=3)))+" V, or"))
    print(("{:<60s}").format("remain interrupted for more than "+str(GRACE_TIME)+" min,"))
    print(("{:<60s}").format("the Pi will be halted & the UPS will power it down.\n"))
else:
#   Not charging.
    print("*** EXTERNAL POWER LOST! RUNNING ON BATTERY POWER!")
    print("*** UPS power timers will be set before shutdown.")
    print("*** When the UPS control script runs again,")
    if (GRACE_TIME==0):
        print("*** the UPS will make the Pi shut down!")
    else:
        print("*** grace time till shutdown will be left: %d min" % GRACE_TIME)
    print()

print(("{:<60s}").format("During normal operation registers 0x18, 0x19 and 0x1A"))
print(("{:<60s}").format("are only set by the upsPlus.py control script in case"))
print(("{:<60s}").format("of power loss and a pending shut down of the Pi."))

if aReceiveBuf[0x18] == 0:
    print('0x18: UPS power down timer not set.')
else:
    print("0x18: UPS power down timer set to: %8.d sec" % (aReceiveBuf[0x18]))
    
if aReceiveBuf[0x19] == 0x01:
    print(("{:<60s}").format("0x19: Automatic restart upon return of external power"))
else:
    print(("{:<60s}").format("0x19: No automatic restart upon return of external power"))

if aReceiveBuf[0x1A] == 0:
    print('0x1A: UPS power up timer not set.')
else:
    print("0x1A: UPS power up timer set to: %8.d sec" % (aReceiveBuf[0x1A]))
print()

print("Accumulated running time:                         %8.d min" % round((aReceiveBuf[0x1F] << 0o30 | aReceiveBuf[0x1E] << 0o20 | aReceiveBuf[0x1D] << 0o10 | aReceiveBuf[0x1C])/60))
print("Accumulated charging time:                        %8.d min" % round((aReceiveBuf[0x23] << 0o30 | aReceiveBuf[0x22] << 0o20 | aReceiveBuf[0x21] << 0o10 | aReceiveBuf[0x20])/60))
print("Current up time:                                  %8.d min" % round((aReceiveBuf[0x27] << 0o30 | aReceiveBuf[0x26] << 0o20 | aReceiveBuf[0x25] << 0o10 | aReceiveBuf[0x24])/60))

print(("{:<s}{:>2d}").format("F/W version:",(aReceiveBuf[0x29] << 0o10 | aReceiveBuf[0x28])))

# Serial Number
UID0 = "%08X" % (aReceiveBuf[0xF3] << 0o30 | aReceiveBuf[0xF2] << 0o20 | aReceiveBuf[0xF1] << 0o10 | aReceiveBuf[0xF0])
UID1 = "%08X" % (aReceiveBuf[0xF7] << 0o30 | aReceiveBuf[0xF6] << 0o20 | aReceiveBuf[0xF5] << 0o10 | aReceiveBuf[0xF4])
UID2 = "%08X" % (aReceiveBuf[0xFB] << 0o30 | aReceiveBuf[0xFA] << 0o20 | aReceiveBuf[0xF9] << 0o10 | aReceiveBuf[0xF8])

print("Serial Number: " + UID0 + "-" + UID1 + "-" + UID2 )
print()
#EOF
