#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# Execute UPS function "0x1B Reset to Factory Defaults 0/1 Bool"
# ar - 08-06-2022, 11-06-2022

import sys
import smbus2
import syslog
import click

# Define I2C bus
DEVICE_BUS = 1

# Define device i2c slave address.
DEVICE_ADDR = 0x17

# Raspberry Pi communicates with MCU via i2c protocol.
bus = smbus2.SMBus(DEVICE_BUS)

print("*"*62)
print(("*** {:^54s} ***").format("-- Perform a reset to factory defaults --"))
print(("*** {:^54s} ***").format("Writing 1 to register 0x1B makes the UPS"))
print(("*** {:^54s} ***").format("reset various settings to default values."))
print(("*** {:^54s} ***").format(">>> 0x1B will automatically be set back to 0 <<<"))
print("*"*62)
print()

if click.confirm('Do you want to continue?', default=True):
    click.echo('Resetting UPS to factory defaults ...')
else:
    print('Script aborted')
    exit()

#exit()

try:
    bus.write_byte_data(DEVICE_ADDR, 0x1B, 0x01)    
    msg = "UPS Plus reset to factory defaults!"
    print(msg)
except Exception as e:
    errmsg = "Error resetting UPS Plus to factory defaults: " + str(e)
    print(errmsg)
    syslog.syslog(syslog.LOG_ERR, errmsg)

# EOF