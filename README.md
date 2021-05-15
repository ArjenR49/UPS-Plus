Scripts for a 52Pi UPS plus v.5


I am a total apprentice at GitHub. I just uploaded these scripts I developed, to the repository so that others can see what I cobbled together. I am probably using GitHub the wrong way to boot ...

Anyway ...
the UPS registers at address 0x17 and offsets 0x18-0x1A I find pretty sensitive to if and when you write to them and in which order probably as well. Don't write to them when it is not necessary, I would say. Not even 0.

The PowerCycle.py script that serves to schedule a full power cycle of the Pi, works OK, but the UPS doesn't always restart the Pi. Most often it works. I haven't gotten to the bottom of that.

Sure enough a little after I left home, the Pi was only shut down by the scheduled PowerCycle.py script, but the power to the Pi wasn't cut. I had to switch it off and on manually using the push button. This has been its behaviour no matter what I do. The minute I look the other way, it malfunctions after numerous power cycles that did proceed as they should ... very weird.

I have added rounding to significant bits, because I don't believe in the accuracy of mV and mA readings ;-) I also like to see Volts and Amps in a report, although I may read them automatically as mA and mV when it is more suitable.

I changed bit-wise shifting operations (<< and >>) to octal notation just because I find it more clear.

I added TimeoutError exception handling to all reads and writes on the I2C bus, except for the INA devices where the values are only used for reporting. In the upsPlus.py code which decides whether to start shutdown, however, there is also exception/error handling for the INA-voltage.

Sometimes my UPS_report.py and also upsPlus.py report the batteries to be discharging even though the charger is connected. This appears to happen when the UPS f/w is doing its data collection about the batteries and shuts off all blue LEDs for a short while every two minutes (=sampling interval). Apparently the batteries are disconnected from the charger during that sampling procedure.

My crontab is intended for stress testing of the power cycle bahaviour of the UPS.
The sleep x && in the line for PowerCycle.py is to make sure it runs after upsPlus.py.
The flock locks are there so make sure they never run and address the same UPS control registers concurrently.

I don't run the original *_iot.py script, because I find it gets in the way with its random delay of up to 59 seconds. upsPlus.py runs every minute ...

The power up and power down values when not 0 should allow enough time for the Pi to shut down in an orderly manner. Depending on what the Pi is doing that may take more or less time.
The UPS is quite unforgiving and has no idea of what the Pi is doing, whether it is ready shutting down. It will just cut power to the Pi when the timer reaches 0, when the time comes.

I intend to run motioneye and VNC (server and client) on this Pi4, but I disabled motioneye for now, so it cannot interfere.

There is probably more to say about my experiences with the UPS and scripting, but it'll have to wait until later.

------------------------------------------------------------

Now running on f/w v.7:
Implemented the watchdog function in upsPlus.py per suggestion from Nick Taterli.
Setting the 'reboot' timer 0x1A to >=120 - I chose 180 - will make the UPS f/w count down to cutting the power to the Pi - abruptly - and reconnect the power after about 9 minutes!
As long as upsPlus.py executes every 60 seconds (cron), the reboot timer 0x1A will be reset to >=120 and the Pi will keep running, because the timer never reaches 0.
However, if the Pi freezes, upsPlus.py will stop updating 0x1A and the reboot timer will eventually reach 0, which is when the UPS bluntly cuts the power.
Register 0x19 needs to be 0 for this to work. Check the code and the comments in upsPlus.py.
Voilá, a watchdog function!

Of course cutting the power like this can damage your file system, but then, what else is there to do if the OS freezes?

You can test the watchdog by temporarily commenting out 'putByte(0x1A, OMR0x1AD)' (currently) on line 75 of upsPlus.py. You can follow the counting down when you run UPS_report.py repeatedly from a terminal until 0x1A reaches 0 (perhaps actually more like 5 seconds) and the power is abruptly cut. Make a clone of your OS before, if you are worried that cutting the power like that may damage your OS. (I would advise using rpi-clone. It will not take much time to update your clone, as it uses rsync.)

Running PowerCycle.py will still also cause power-off and power on after 9 minutes, but it will do a shutdown of the OS before cutting the power. Take care the power-off timer value is large enough to allow your Pi to shutdown in an orderly manner, as the UPS has no clue about the state of the Pi or its OS.
Thirty seconds may seem long enough, but in some circumstances a Pi might take longer. I prefer longer power-off delays.
The delay until restart used to be 5 seconds on f/w v.5, but it is now a surprising 9 minutes.

