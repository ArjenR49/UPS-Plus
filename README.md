Scripts for a 52Pi UPS plus v.5


I am a total apprentice at GitHub. I just uploaded these scripts I developed, to the repository so that others can see what I cobbled together. I am probably using GitHub the wrong way to boot ...

Anyway ...
the UPS registers at address 0x17 and offsets 0x18-0x1A I find pretty sensitive to if and when you write to them and in which order probably as well. Don't write to them when it is not necessary, I would say. Not even 0.

The PowerCycle.py script that serves to schedule a full power cycle of the Pi, works OK, but the UPS doesn't always restart the Pi. Most often it works. I haven't gotten to the bottom of that.

Sure enough a little after I left home, the Pi was only shut down by the scheduled PowerCycle.py script, but the power to the Pi wasn't cut. I had to switch it off and on manually using the push button. This has been its behaviour no matter what I do. The minute I look the other way, it malfunctions after numerous power cycles that did proceed as they should ... very weird.

I have added rounding to significant bits, because I don't believe in the accuracy of mV and mA readings ;-) I also like to see Volts and Amps in a report, although I may read them automatically as mA and mV when it is more suitable.

I changed bit-wise shifting operations (<< and >>) to octal notation just because I find it more clear.

I added TimeoutError exception handling to all reads and writes on the I2C bus, except for the INA devices. They don't seem to cause problems.
Sometimes my UPS_report reports the batteries to be discharging even though the charger is connected. This happens when the UPS f/w is doing its data colllection about the batteries and shuts off all blue LEDs every two minutes (=sampling interval).

My crontab is intended for stress testing of the power cycle bahaviour of the UPS.
The sleep x && in the line for PowerCycle.py is to make sure it runs after upsPlus.py.
The flock locks are there so make sure they never run and address the same UPS control registers concurrently.

I don't run the original *_iot.py script, because I find it gets in the way with its random delay of up to 59 seconds. upsPlus.py runs every minute ...

The power up and power down values when not 0 should allow enough time for the Pi to shut down in an orderly manner. Depending on what the Pi is doing that may take more or less time.
The UPS is quite unforgiving and has no idea of what the Pi is doing, whether it is ready shutting down. It will just cut power to the Pi when the timer reaches 0, when the time comes.

I intend to run motioneye and VNC (server and client) on this Pi4, but I disabled motioneye for now, so it cannot interfere.

There is probably more to say about my experiences with the UPS and scripting, but it'll have to wait until later.
