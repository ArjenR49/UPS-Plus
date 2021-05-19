Scripts for a 52Pi UPS plus v.5


I am a total apprentice at GitHub. I just uploaded these scripts I developed, to the repository so that others can see what I cobbled together. I am probably using GitHub the wrong way to boot ...

Anyway ...
For best operation all around the UPS registers at address 0x17 and offsets 0x18-0x1A need to be set with thought.

My PowerCycle.py script can be scheduled to do a full power cycle of the Pi combined with a proper shutdown. It is debatable if you need a script to do a power cycle, as a frozen Pi will obviously not be able to start it. If you like to to reboot the Pi at regular intervals just to make sure, you can simply schedule an ordinary reboot command, of course.
There's a watchdog function which is enabled in upsPlus.py for cases where the Pi freezes. See below.
Under f/w v.5 the UPS used to restore power to the Pi already 5 seconds after cutting the power as a result of running PowerCycle.py. It was a surprise to see that delay lengthened to ca. 10 minutes after the upgrade to f/w v.7.

My version of upsPLus.py has rounding to significant bits of the reported electrical units, because I don't believe in the accuracy of mV and mA readings as originally presented ;-) I also prefer to see Volts and Amps in a report, although I may read them automatically as mA and mV when it is more suitable.
Out of the full feature script I made a script that reports just about everything there is to now about the surrent state of the UPS. It applies the same rounding to its output.

I changed bit-wise shifting operations (<< and >>) to octal notation just because I find it more clear.

I added TimeoutError exception handling to all reads and writes on the I2C bus, except for some reads concerning the INA devices where the values are only used for reporting. In the upsPlus.py code which decides whether to start shutdown, however, there is also exception/error handling for the INA-voltage.

Sometimes UPS_report.py (and also upsPlus.py) show the batteries to be discharging even though the charger is connected and powered. This happens when the UPS f/w is doing its data collection about the batteries. While this is going on the UPS shuts off all blue LEDs for a short while every two minutes (=sampling interval, by default every 2 minutes). Apparently the batteries are disconnected from the charger during the sampling procedure and the Pi powered from the batteries.

My crontab is intended for stress testing of the power cycle behaviour of the UPS, and the I2C bus.
The 'sleep x &&' in the line for PowerCycle.py is to make sure it runs after upsPlus.py.
The flock locks are there so make sure they never run and address the same UPS control registers concurrently.
A condition involving the current time is intended to keep upsPlus.py (and PowerCycle.py) from running when BackinTime is scheduled to run.

I don't run the original *_iot.py script on a cron schedule. It has a delay built in of up to 59 seconds. If you prevent it from running concurrently with upsPlus.py and v.v., because of the I2C bus, it maydelay upsPlus.py. I find it gets in the way. I can run it occasionally.

The power-up and power-down timer values when not =0 must allow enough time for the Pi to shut down in an orderly manner. I have occasionally observed long shutdown times on a Pi.
As the UPS has no idea of what the Pi is doing, whether it is finished shutting down or not, is quite unforgiving. It will just cut power to the Pi when either countdown timer reaches 0.

I intend to run motioneye and VNC (server and client) on this Pi4.

------------------------------------------------------------

Now running on f/w v.7:

Implemented a watchdog function with two different modes in upsPlus.py per suggestion from Nick Taterli.

Setting either timer 0x18 or 0x1A to >=120 - I chose 180 - will make the UPS f/w count down to cutting the power to the Pi, unless upsPlus.py runs every minute.
As long as upsPlus.py executes every 60 seconds (cron), the timer 0x18 or 0x1A will be reset to the starting value of >=120 and the Pi will keep running, because the timer never reaches 0.
However, if the Pi freezes, upsPlus.py will stop updating the timer and the reboot timer in the UPS will eventually reach 0, which is when the UPS abruptly cuts the power.
Register 0x19 needs to be =0 for this to work. Check the code and the comments in upsPlus.py.
There are two modes:
If 0x1A is set to >= 120, the UPS will reconnect the power after about 10 minutes and the Pi will restart!
If on the other hand you choose to set 0x18 to >=120, there is no auto-restart. Start by pressing the UPS button.
It's not useful to set both countdown timers. 

Voilá, a watchdog function! With or without auto-restart.

Of course cutting the power like this can damage your file system, but then, what else is there to do if the OS freezes?

You can test the watchdog by temporarily commenting out either 'putByte(0x1A, OMR0x1AD)' or 'putByte(0x18, OMR0x18D)' (currently around line 75) of upsPlus.py. You can then observe the countdown by running UPS_report.py repeatedly from a terminal until 0x18 or 0x1A reaches 0 (perhaps actually more like 5 seconds) and the power is abruptly cut. Make a clone of your OS beforehand, if you are worried that cutting the power abruptly may damage your OS. (I would advise using rpi-clone. It will not take much time to update your clone, as it uses rsync and will copy only the changes.)

Running PowerCycle.py will also cause power-off and power-on after 10 minutes, but it will first do a shutdown of the OS before cutting the power. Make the power-off timer value large enough to allow your Pi to shutdown in an orderly manner, as the UPS has no clue about the state of the Pi or its OS.
Thirty seconds may seem long enough, but in some circumstances a Pi might take longer. I prefer at least 60 seconds or more.
The delay until restart used to be 5 seconds on f/w v.5, but it is now a surprising 10 minutes or so. The firmware developers at Geekpi may provide options to change this and make the button responsive during the 10 minute startup delay.

During the ca. 10 minutes startup delay, my (Sanyo NCR18650GA 3450 mAh Li-Ion) batteries get charged to the full and also the last of the 4 blue LEDs stops blinking.

---------------------------------------
There was an error in the exception handling which caused UPS_report to occasionally fail with the following:

pi@RPI-HUB:~ $ python3 $HOME/UPS+/UPS_report.py
*** Data from INA219 at 0x40:
Raspberry Pi supply voltage:                         4.920 V
Raspberry Pi current consumption:                    2.290 A
Raspberry Pi power consumption:                     10.700 W

*** Data from INA219 at 0x45:
Battery voltage:                                     4.130 V
Battery current (discharging):                       2.900 A
Battery power consumption:                          12.100 W

i= 225
Traceback (most recent call last):
  File "/home/pi/UPS+/UPS_report.py", line 80, in <module>
    aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
  File "/home/pi/.local/lib/python3.7/site-packages/smbus2/smbus2.py", line 433, in read_byte_data
    ioctl(self.fd, I2C_SMBUS, msg)
TimeoutError: [Errno 110] Connection timed out

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/pi/UPS+/UPS_report.py", line 84, in <module>
    print('byte read=', aReceiveBuf[i], ' error:', e)
IndexError: list index out of range
pi@RPI-HUB:~ $

As the same code is used in upsPLus.py, I suspect this bug to also have caused an occasional failure to restart the Pi after a scheduled PowerCycle.py.
The 'list index (to aReceiveBuf[i]) out of range' is obviously because byte 225 which was the subject of the attempted read, hadn't been added to the list aReceiveBuf, i.e. the list element with i=225 hadn't been created yet. Anyway, the remedy is, don't try to print what doesn't yet exist.

TimeoutError exceptions are rare, but they do happen from time to time. My tests with the scripts called CatchExceptions proved that (to me). My attempts at exception handling are those of an amateur copycat ...

Testing continues ...

-----------------------------------

Through an oversight exception handling was missing from the putByte function in upsPlus.py, which must have been the reason that occasionally I observed (UPS_report) the countdown timer 0x18 counting down from 180 right past 120. Of course, after another execution of upsPlus.py this situation would be corrected, but it was odd. The recently observed TimeoutError in UPS_report.py already made it very clear that SMBus exception handling is essential in all cases. It should be mandatory, really.
I added exception handling for TimeoutError to putByte() in upsPlus and the same putByte() definition is now also used in PowerCycle.py.

Despite looking at the UPS_event.log a million times, upsPlus.py still had one wrong unit in its printed output (>>UPS_event.log ), viz. A for power. This was corrected.

The restart delay after a 'watchdog with restart' event or a 'power cycle' is actually less than 10 minutes, more like 8-9 minutes. 
  
---------------
  
After more testing using a new test script CatchExceptions.py, I found that rather often a write to a register apparently doesn't succeed and it gets to keep its previous value. This, of course, is a recipe for trouble. 
If you run the said script on its own, keeping a terminal ready with upsPlus.py on the command line to return the register used in the test to normalcy, you can see for yourself, if your UPS exhibits write failures.
I wrote failure, as they're not an 'exception' in the python sense. It's just that when you attempt to change the content of a register, it doesn't take.
My prescription is to write a byte, read it back, compare the results and write again, if they're different until the write sticks, so to say.
The bad write and failing comparison 'raise' a Value Error exception in the script. 
I have amended both my upsPlus.py and my PowerCycle.py scripts to hammer the byte until it sticks:

# Write byte to specified I2C register address 'until it sticks'.
def putByte(RA, wbyte):
    while True:
        try:
            with SMBus(DEVICE_BUS) as pbus:
                pbus.write_byte_data(DEVICE_ADDR, RA, wbyte)
            with SMBus(DEVICE_BUS) as gbus:
                rbyte = gbus.read_byte_data(DEVICE_ADDR, RA)
            if (wbyte) <= rbyte <= (wbyte):
                print("OK ", wbyte, rbyte)
                break
            else:
                raise ValueError
        except ValueError:
            print("Write:", wbyte, "!= Read:", rbyte, " Trying again")
            pass

It is also noteworthy that writing to a timer register (0x18, 0x1A), when its old value is not 0 seems problematic. Such a register is constantly being decremented by the f/w, which may be why changing it to anything else than 0, proved not very reliable. So I added 'reset to 0' commands to my scripts whenever the ultimate intent is to write a value other than 0 and the current content could be anything. Probably sounds complicated, but I can now have the UPS run overnight and have it do a PowerCycle twice an hour and still find the Pi running in the morning (unless it has just started the powercycle). Restart initiated by PowerCycle.py takes ca. 10 minutes which cannot be controlled by the user.
There's no telling how this all may change whenever there's a new f/w, of course. The jump from v.5 to v.7 brought a lengthening of the restart (elicited by timer 0x1A) from 5 seconds to 10 minutes, just like that.

