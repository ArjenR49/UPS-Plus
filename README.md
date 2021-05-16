Scripts for a 52Pi UPS plus v.5


I am a total apprentice at GitHub. I just uploaded these scripts I developed, to the repository so that others can see what I cobbled together. I am probably using GitHub the wrong way to boot ...

Anyway ...
For best operation all around the UPS registers at address 0x17 and offsets 0x18-0x1A need to be set with thought.

The current PowerCycle.py script serves to schedule a full power cycle of the Pi combined with a proper shutdown. It is debatable if you need it. With f/w v.7 the start up of the power cycle is delayed by ca. 10 minutes, which is surprising. Under v.5 the UPS used to reapply power to the Pi already 5 seconds after cutting the power.

In the scripts I have added rounding to significant bits of the reported electrical units, because I don't believe in the accuracy of mV and mA readings as originally presented ;-) I also prefer to see Volts and Amps in a report, although I may read them automatically as mA and mV when it is more suitable.

I changed bit-wise shifting operations (<< and >>) to octal notation just because I find it more clear.

I added TimeoutError exception handling to all reads and writes on the I2C bus, except for the INA devices where the values are only used for reporting. In the upsPlus.py code which decides whether to start shutdown, however, there is also exception/error handling for the INA-voltage.

Sometimes my UPS_report.py and also upsPlus.py report the batteries to be discharging even though the charger is connected. This happens when the UPS f/w is doing its data collection about the batteries and shuts off all blue LEDs for a short while every two minutes (=sampling interval). Apparently the batteries are disconnected from the charger during that sampling procedure.

My crontab is intended for stress testing of the power cycle bahaviour of the UPS.
The sleep x && in the line for PowerCycle.py is to make sure it runs after upsPlus.py.
The flock locks are there so make sure they never run and address the same UPS control registers concurrently.

I don't run the original *_iot.py script, because I find it gets in the way with its random delay of up to 59 seconds. upsPlus.py runs every minute ...

The power up and power down timer values when not 0 should allow enough time for the Pi to shut down in an orderly manner. Depending on what the Pi is doing that may take more or less time.
The UPS is quite unforgiving and has no idea of what the Pi is doing, whether it is ready shutting down. It will just cut power to the Pi when the timer reaches 0, when the time comes.

I intend to run motioneye and VNC (server and client) on this Pi4.

------------------------------------------------------------

Now running on f/w v.7:

Implemented a watchdog function with two different modes in upsPlus.py per suggestion from Nick Taterli.
Setting either timer 0x18 or 0x1A to >=120 - I chose 180 - will make the UPS f/w count down to cutting the power to the Pi - abruptly ...
If 0x1A is set to >= 120, the UPS will reconnect the power after about 10 minutes and the Pi will restart automatically!
If you choose to set 0x18 to >=120, there is no auto-restart. Start by pressing the UPS button.

As long as upsPlus.py executes every 60 seconds (cron), the timer 0x18 or 0x1A will be reset to >=120 and the Pi will keep running, because the timer never reaches 0.
However, if the Pi freezes, upsPlus.py will stop updating the timer and the reboot timer will eventually reach 0, which is when the UPS bluntly cuts the power.
Register 0x19 needs to be 0 for this to work. Check the code and the comments in upsPlus.py.
Voilá, a watchdog function! Either with or without auto-restart.

Of course cutting the power like this can damage your file system, but then, what else is there to do if the OS freezes?

You can test the watchdog by temporarily commenting out either 'putByte(0x1A, OMR0x1AD)' or 'putByte(0x18, OMR0x18D)' (currently around line 75) of upsPlus.py. You can follow the counting down by running UPS_report.py repeatedly from a terminal until 0x18 or 0x1A reaches 0 (perhaps actually more like 5 seconds) and the power is abruptly cut. Make a clone of your OS beforehand, if you are worried that cutting the power abruptly may damage your OS. (I would advise using rpi-clone. It will not take much time to update your clone, as it uses rsync and will copy only the changes.)

Running PowerCycle.py will also cause power-off and power-on after 10 minutes, but it will first do a shutdown of the OS before cutting the power. Make the power-off timer value large enough to allow your Pi to shutdown in an orderly manner, as the UPS has no clue about the state of the Pi or its OS.
Thirty seconds may seem long enough, but in some circumstances a Pi might take longer. I prefer longer power-off delays 60 seconds or more.
The delay until restart used to be 5 seconds on f/w v.5, but it is now a surprising 9 minutes.
