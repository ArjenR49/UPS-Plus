#!/usr/bin/python3
# -*- coding: utf-8 -*-

# adapted from scripts provided at GitHub: Geeekpi/upsplus by nickfox-taterli
# ar - 25-05-2021, 19-07-2021, 10-08-2021

import locale
# Set to Dutch locale to get comma decimal separator
#locale.setlocale(locale.LC_NUMERIC, 'nl_NL.UTF-8')
# Set to system default locale (enable number formatting using decimal separator for the locale)
locale.setlocale(locale.LC_ALL, '')

from smbus2 import SMBus
from datetime import datetime, timezone
from math import log10, floor
from ina219 import INA219, DeviceRangeError

PROTECTION_VOLTAGE_MARGIN_mV=float(200)  # mV
PROTECTION_VOLTAGE_MARGIN_mV=PROTECTION_VOLTAGE_MARGIN_mV/1000  # convert to V

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

# Instance INA219 and getting information from it.
#ina = INA219(0.00725, busnum=DEVICE_BUS, address=0x40)  # Value given by GeeekPi 
#ina = INA219(0.011, busnum=DEVICE_BUS, address=0x40)  # Experimental value
ina = INA219(0.0145, busnum=DEVICE_BUS, address=0x40)
ina.configure()
#ina.configure(ina.RANGE_16V, ina.GAIN_2_80MV, ina.ADC_128SAMP, ina.ADC_128SAMP)

print(("-------- {:^43s} ---------").format(TimeStampA))
print()
print("*** Data from INA219 at 0x40:")
#print("Raspberry Pi supply voltage:                      %8.3f V" % round_sig(ina.voltage(),n=3))
print(locale.format_string("Raspberry Pi supply voltage:                      %8.3f V",round_sig(ina.voltage(),n=3)))
print(locale.format_string("Raspberry Pi current consumption:                 %8.3f A",round_sig(ina.current()/1000,n=3)))
print(locale.format_string("Raspberry Pi power consumption:                   %8.3f W", round_sig(ina.power()/1000,n=3)))
print()


#ina = INA219(0.005, busnum=DEVICE_BUS, address=0x45)  # Value given by GeeekPi
ina = INA219(0.011, busnum=DEVICE_BUS, address=0x45)  # Experimental value
ina.configure()
#ina.configure(ina.RANGE_16V, ina.GAIN_2_80MV, ina.ADC_128SAMP, ina.ADC_128SAMP)
print("*** Data from INA219 at 0x45:")
print(locale.format_string(        "Battery voltage:                                  %8.3f V", round_sig(ina.voltage(),n=3)))
try:
    if ina.current() > 0:
        print(locale.format_string("Battery current (charging):                       %8.3f A", round_sig(abs(ina.current()/1000),n=3)))
        print(locale.format_string("Power supplied to the batteries:                  %8.3f W", round_sig(ina.power()/1000,n=3)))
    else:
        print(locale.format_string("Battery current (discharging):                    %8.3f A", round_sig(abs(ina.current()/1000),n=2)))
        print(locale.format_string("Battery power consumption:                        %8.3f W", round_sig(ina.power()/1000,n=3)))
except DeviceRangeError:
    print('INA219 at 0x45: Out of Range Warning!')
    print('BATTERY CURRENT POSSIBLY EXCEEDING SAFE LIMITS!')
# Keep sampling in case of another type of error
except:
    pass
finally:
    print()

aReceiveBuf = []
aReceiveBuf.append(0x00)

i = 0x01
while i < 0x100:
    try:
        with SMBus(DEVICE_BUS) as bus:
            aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
            i += 1
    except Exception as e:
        raise Exception("[UPS_report] Error reading UPS registers: " + str(e))

print( "*** Remainder of report is based on data collected")
print(("*** by the UPS f/w and read from memory at 0x{:02X}").format(DEVICE_ADDR))
#print( "--- except value(s) marked with *")
print()
print(locale.format_string("UPS board MCU voltage:                              %6.3f V", round_sig((aReceiveBuf[0x02] << 0o10 | aReceiveBuf[0x01])/1000,n=3)))
print(locale.format_string("Voltage at Pi GPIO header pins:                     %6.3f V", round_sig((aReceiveBuf[0x04] << 0o10 | aReceiveBuf[0x03])/1000,n=3)))

print(locale.format_string("USB type C port input voltage:                      %6.3f V", round_sig((aReceiveBuf[0x08] << 0o10 | aReceiveBuf[0x07])/1000,n=3)))
print(locale.format_string("Micro USB port input voltage:                       %6.3f V", round_sig((aReceiveBuf[0x0A] << 0o10 | aReceiveBuf[0x09])/1000,n=3)))

print()
# Learned from the battery internal resistance change, the longer the use, the more stable the data:
print(locale.format_string("Battery temperature (estimate):                     %6.d°C" , round_sig(aReceiveBuf[0x0C] << 0o10 | aReceiveBuf[0x0B])))

#print()
print("Automatic detection of battery type                    " + ("yes" if not aReceiveBuf[0x2A] else " no"))

# Fully charged voltage is learned through charging and discharging:
print(locale.format_string("Batteries fully charged at (UPS/learned value):     %6.3f V", round_sig((aReceiveBuf[0x0E] << 0o10 | aReceiveBuf[0x0D])/1000,n=3)))

# This value is inaccurate during charging:
print(locale.format_string("Current voltage at battery terminals:               %6.3f V", round_sig((aReceiveBuf[0x06] << 0o10 | aReceiveBuf[0x05])/1000,n=3)))

# The deep discharge limit value is stored in memory at 0x11-0x12 based on the user's own preference:
# DISCHARGE_LIMIT (a.k.a. protection voltage):
DISCHARGE_LIMIT=(aReceiveBuf[0x12] << 0o10 | aReceiveBuf[0x11])/1000
print(locale.format_string("Discharge limit for use by the control script:      %6.3f V", round_sig(DISCHARGE_LIMIT,n=3)))

# Fully discharged voltage is learned through charging and discharging.
# A.k.a. empty voltage, at which the UPS f/w will cut power delivery to the Pi, if it comes to that:
print(locale.format_string("Batteries fully discharged at (UPS/learned value):  %6.3f V", round_sig((aReceiveBuf[0x10] << 0o10 | aReceiveBuf[0x0F])/1000,n=3)))

# At least one complete charge and discharge cycle needs to pass before this value is meaningful:
print(locale.format_string("Estimated remaining battery capacity:             %8.d %%", (aReceiveBuf[0x14] << 0o10 | aReceiveBuf[0x13])))

# For a few seconds all blue charging level LEDs are off
# and only the batteries deliver power to the Pi
# as sampling of battery characteristics takes place.
# The interval between sampling events is normally 2 minutes.
print(locale.format_string("Battery sampling ('blue LEDs off') interval:      %8.d min", (aReceiveBuf[0x16] << 0o10 | aReceiveBuf[0x15])))

print()
if aReceiveBuf[0x17] == 1:
    print("Current power state: normal")
else:
    print("Current power state: other")

print()
if (aReceiveBuf[0x08] << 0o10 | aReceiveBuf[0x07]) > 4000:
    print('External power is connected to the USB type C input.\n')
    print("Should the external power be interrupted long enough")
    print(locale.format_string("to cause the battery voltage to drop below %.3g V \n" +\
                               "+ %.3g V as a safety margin, an appropriate control script", \
                               (DISCHARGE_LIMIT, PROTECTION_VOLTAGE_MARGIN_mV)))
    print("should halt the Pi, after which the UPS may eventually")
    print("power it down depending on the value of 0x18/0x1A.\n")
elif (aReceiveBuf[0x0A] << 0o10 | aReceiveBuf[0x09]) > 4000:
    print('External power is connected to the micro USB input.\n')
    print("Should the external power be interrupted long enough")
    print(locale.format_string("to cause the battery voltage to drop below %.3g V \n" +\
                               "+ %.3g V as a safety margin, an appropriate control script", \
                               (DISCHARGE_LIMIT, PROTECTION_VOLTAGE_MARGIN_mV)))
    print("should halt the Pi, after which the UPS may eventually")
    print("power it down depending on the value of 0x18/0x1A.\n")
else:
#   Not charging.
    print("*** EXTERNAL POWER LOST! RUNNING ON BATTERY POWER!")
    print()
    print("Should the external power be interrupted long enough")
    print(locale.format_string("to cause the battery voltage to drop below %.3g V \n" +\
                               "+ %.3g V as a safety margin, an appropriate control script", \
                               (DISCHARGE_LIMIT, PROTECTION_VOLTAGE_MARGIN_mV)))
    print("should halt the Pi, after which the UPS")
    print("may eventually power it down.\n")
    print("UPS power off/on timer registers 0x18 and 0x1A")
    print("and register 0x19 should be set to values appropriate")
    print("for a power failure event by the control script")
    print("immediately before halting the Raspberry Pi.")
    print()


print(("{:<60s}").format("Current values of the UPS power control registers:\n"
                         +    "0x18=" + str(aReceiveBuf[0x18])
                         + " / 0x19=" + str(aReceiveBuf[0x19])
                         + " / 0x1A=" + str(aReceiveBuf[0x1A])
                         + "\nExplanation:"))
if aReceiveBuf[0x18] == 0:
    print('0x18 - Power off timer (no restart)   - not set.')
else:
    print("0x18 - Power off timer (no restart)   - set to: %3.d sec" % (aReceiveBuf[0x18]))
    
print(("0x19 - Automatic restart upon return of external power: ") + ("yes" if aReceiveBuf[0x19] else "no"))
     
if aReceiveBuf[0x1A] == 0:
    print('0x1A - Power off timer (with restart) - not set.')
else:
    print("0x1A - Power off timer (with restart) - set to: %3.d sec" % (aReceiveBuf[0x1A]))
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

