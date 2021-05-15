#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 15-05-2021

# ''' UPS Plus v.5 control script '''

import os
import time
from smbus2 import SMBus
from math import log10, floor
from ina219 import INA219, DeviceRangeError
from datetime import datetime, timezone

# Essential UPS I2C power control register settings
# (name format: Operation Mode, offset, purpose)
# Default values (normal operation):
OMR0x18D = 0    # seconds, power-off delay
OMR0x19D = 0    # boolean, automatic restart (1) or not (0) after ext. power failure
OMR0x1AD = 180  # seconds, power-on delay (for watchdog function >=120 as suggested by Nick Tater)
# Shutdown event values:
OMR0x18S = 60   # seconds, power-off delay
OMR0x19S = 1    # boolean, automatic restart (1) or not (0) after ext. power failure
OMR0x1AS = 0    # seconds, power-on delay

# Define I2C bus
DEVICE_BUS = 1

# Define device I2C slave address.
DEVICE_ADDR = 0x17

# Set threshold for UPS automatic power-off to prevent
# destroying the batteries by excessive discharge (unit: mV).
# DISCHARGE_LIMIT (a.k.a. protection voltage) will be stored in memory at 0x11-0x12
DISCHARGE_LIMIT = 3000

# Set threshold for UPS power-off conserving battery power &
# providing ability to overcome possibly repeated blackouts (unit: mV).
POWEROFF_LIMIT = 3500
# POWEROFF_LIMIT = DISCHARGE_LIMIT

# Keep Pi running for maximum <GRACE_TIME> 'units' of time after blackout
# (unit = upsPlus.py cron job interval, normally 1 min)
GRACE_TIME = 1440
GRACE_TIME = 5
# Minimum practical value is 2 ...
GRACE_TIME = max(GRACE_TIME, 2)

# Set the sample period, unit: min (usually 2).
SAMPLE_TIME = 2

# Path for parameter files
PATH = str(os.getenv('HOME'))+'/UPS+/'

# Record starting time
StartTime = datetime.now(timezone.utc).astimezone()
TimeStampA = '{:%d-%m-%Y %H:%M:%S}'.format(StartTime)
TimeStampB = '{:%Y-%m-%d_%H:%M:%S}'.format(StartTime)

# Rounding to n significant digits
def round_sig(x, n=3):
    if not x:
        return 0
    power = -floor(log10(abs(x))) + (n - 1)
    factor = (10 ** power)
    return round(x * factor) / factor

def putByte(RA, byte):
    with SMBus(DEVICE_BUS) as pbus:
        pbus.write_byte_data(DEVICE_ADDR, RA, byte)

# Initialize UPS power control registers
putByte(0x19, OMR0x19D)
putByte(0x1A, OMR0x1AD)
putByte(0x18, OMR0x18D) 

# Save POWEROFF_LIMIT to text file for sharing with other scripts
f = open(PATH+'PowerOffLimit.txt', 'w')
f.write("%s" % POWEROFF_LIMIT)
f.write("\n")
f.close()

# Store DISCHARGE_LIMIT (a.k.a. protection voltage) in memory at 0x11-0x12
try:
    with SMBus(DEVICE_BUS) as bus:
        bus.write_byte_data(DEVICE_ADDR, 0x11, DISCHARGE_LIMIT & 0xFF)
        bus.write_byte_data(DEVICE_ADDR, 0x12,
                                (DISCHARGE_LIMIT >> 0o10) & 0xFF)
except TimeoutError as e:
    print(e)
    time.sleep(0.1)

# Create instance of INA219 and extract information
ina = INA219(0.00725, address=0x40)
ina.configure()
print("="*60)
print(("------ {:^46s} ------").format(TimeStampA))
print(("------ {:^46s} ------").format("Power supplied to Raspberry Pi"))
print("-"*60)
print(("{:<50s}{:>8.3f}{:>2s}").format("Raspberry Pi supply voltage:",
                                       round_sig(ina.voltage(), n=3), " V"))
print(("{:<50s}{:>8.3f}{:>2s}").format("Raspberry Pi current consumption:",
                                       round_sig(ina.current()/1000, n=3),
                                       " A"))
print(("{:<50s}{:>8.3f}{:>2s}").format("Raspberry Pi power consumption:",
                                       round_sig(ina.power()/1000, n=3), " W"))
print("-"*60)

# Battery information
ina = INA219(0.005, address=0x45)
ina.configure()
print(("------ {:^46s} ------").format("UPS Plus batteries"))
print("-"*60)
print(("{:<50s}{:>8.3f}{:>2s}").format("Battery voltage (from INA219):",
                                       round_sig(ina.voltage(), n=3), " V"))
try:
    if ina.current() > 0:
        print(("{:<50s}{:>8.3f}{:>2s}").
              format("Battery current (charging):",
                     abs(round_sig(ina.current()/1000, n=2)), " A"))
        print(("{:<50s}{:>8.3f}{:>2s}").
              format("Power supplied to the batteries:",
                     round_sig(ina.power()/1000, n=3), " A"))
    else:
        print(("{:<50s}{:>8.3f}{:>2s}").
              format("Battery current (discharging):",
              abs(round_sig(ina.current()/1000, n=2)), " A"))
        print(("{:<50s}{:>8.3f}{:>2s}").
              format("Battery power consumption:",
              round_sig(ina.power()/1000, n=3), " W"))
except DeviceRangeError:
    print("-"*60)
    print('INA219: Out of Range Warning!')
    print('BATTERY CURRENT POSSIBLY EXCEEDING SAFE LIMITS!')

print("-"*60)

aReceiveBuf = []
aReceiveBuf.append(0x00)

i = 0x01
while i < 0x100:
    try:
        with SMBus(DEVICE_BUS) as bus:
            aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
            i += 1
    except TimeoutError as e:
        print(i, ' - ', aReceiveBuf[i], ' - ', e)
        time.sleep(0.1)

print()
while False:
    if aReceiveBuf[0x19] == 0x01:
        print(("{:^60s}").
              format("Currently set to restart following a UPS initiated \
              shutdown"))
        print(("{:^60s}").format("as soon as external power returns.\n"))
    else:
        print(("{:^60s}").
              format("Currently not set to restart after a UPS initiated \
              shutdown!\n"))

UID0 = "%08X" % (aReceiveBuf[0xF3] << 0o30 | aReceiveBuf[0xF2] << 0o20 |
                 aReceiveBuf[0xF1] << 0o10 | aReceiveBuf[0xF0])
UID1 = "%08X" % (aReceiveBuf[0xF7] << 0o30 | aReceiveBuf[0xF6] << 0o20 |
                 aReceiveBuf[0xF5] << 0o10 | aReceiveBuf[0xF4])
UID2 = "%08X" % (aReceiveBuf[0xFB] << 0o30 | aReceiveBuf[0xFA] << 0o20 |
                 aReceiveBuf[0xF9] << 0o10 | aReceiveBuf[0xF8])
print(("{:^60s}").format('UID: ' + UID0 + '-' + UID1 + '-' + UID2))
print('*'*60)

print(("{:^60s}").format("UPS power control registers:  "
                         + "0x18=" + str(aReceiveBuf[0x18])
                         + " / 0x19=" + str(aReceiveBuf[0x19])
                         + " / 0x1A=" + str(aReceiveBuf[0x1A])))
print()

# Update initial GRACE_TIME value to file whenever external power is present
if ((aReceiveBuf[0x08] << 0o10 | aReceiveBuf[0x07]) > 4000) | \
   ((aReceiveBuf[0x0A] << 0o10 | aReceiveBuf[0x09]) > 4000):
    f = open(PATH+'GraceTime.txt', 'w')
    f.write("%s" % GRACE_TIME)
    f.close()

if (aReceiveBuf[0x08] << 0o10 | aReceiveBuf[0x07]) > 4000:
    print(("{:^60s}").format('Charging via USB type C connector\n'))
    print(("{:^60s}").
          format("If a power failure lasts for longer than " +
          str(GRACE_TIME)+" min,"))
    print(("{:^60s}").
          format("the UPS will halt the OS/Pi and then power it off."))
    print('*'*60, "\n")
elif (aReceiveBuf[0x0A] << 0o10 | aReceiveBuf[0x09]) > 4000:
    print(("{:^60s}").format('Charging via micro USB connector\n'))
    print(("{:^60s}").
          format("If a power failure lasts for longer than " +
          str(GRACE_TIME)+" min,"))
    print(("{:^60s}").
          format("the UPS will halt the Pi and then power it off."))
else:
    # Read GRACE_TIME from file, decrease by 1 and write back to file
    f = open(PATH+'GraceTime.txt', 'r')
    GRACE_TIME = int(f.read())-1
    f.close()

    print(("*** {:^52s} ***").
          format("EXTERNAL POWER LOST! RUNNING ON BATTERY POWER!"))
    print(("*** {:^52s} ***").format(" "))
    print(("*** {:^52s} ***").
          format("UPS set to power-off at: " +
          str(round_sig(float(POWEROFF_LIMIT)/1000, n=3)) + " V"))
    print(("*** {:^52s} ***").
          format("Battery deep discharge limit set at: " +
          str(round_sig(float(DISCHARGE_LIMIT)/1000, n=3)) + " V"))
    print(("*** {:^52s} ***").
          format("Grace time left till shutdown: " + str(GRACE_TIME) + " min"))
    print('*'*60, "\n")

    # After loss of external power buffered data saving &
    # subsequent shutdown of the Pi followed by UPS' power down
    # will be initiated on one or more of the following conditions:
    # 1. Expiry of the grace period,
    # 2. The battery voltage dropped below 200 mV above discharge protection
    # limit, or
    # 3. The battery voltage dropped below the UPS power-off voltage limit.
    # The script will set the UPS' power down timer initiating
    # a UPS' power down, which allows the Pi time to save buffered data
    # and halt.
    while True:
        try:
            INA_VOLTAGE = ina.voltage()
            # Catch erroneous battery voltage value
            if INA_VOLTAGE == 0:
                raise ValueError
            break
        except ValueError:
            time.sleep(0.1)
            continue

    if (
          (GRACE_TIME <= 0) or
          ((INA_VOLTAGE * 1000) <= max((DISCHARGE_LIMIT + 200),
           POWEROFF_LIMIT))
           ):
        print('#'*60)
        print('External power to the UPS has been lost,')
        print('the power lost grace period expired, or the battery voltage')
        print('either dropped below the UPS\' power-off voltage limit,')
        print('or is about to drop below the deep discharge limit ...')
        print('Shutting down the Raspberry Pi & powering off ...')

        # Enable automatic restart on return of external power
        # Enable: write 1 to register 0x19
        # Disable: write 0 to register 0x19
        putByte(0x19, OMR0x19S)

        # Unset UPS power up timer (unit: seconds).
        putByte(0x1A, OMR0x1AS)

        # Set UPS power down timer (unit: seconds)
        # allowing the Pi time to sync & shutdown.
        putByte(0x18, OMR0x18S)

        time.sleep(2)  # Allow UPS F/W to adjust to the new settings.

        # UPS will cut power to the Pi after the UPS' power down
        # timer period has expired allowing the Pi to sync and then halt.
        os.system("sudo shutdown now")
        # Script continues executing, indefinitely as it were,
        # until it is eventually killed by the Pi shutting down.
        while True:
            time.sleep(10)
    # Control is now left to the UPS' F/W and MCU ...
    # Otherwise update GRACE_TIME on file and end script execution.
    else:
        f = open(PATH+'GraceTime.txt', 'w')
        f.write("%s" % (GRACE_TIME))
        f.close()

# EOF