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
