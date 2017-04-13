Raspberry Pi Nixie Tube Driver led and nixie controller
=============================================================================

This Raspberry Pi Nixie Tube Driver is for the board from this kickstarter:
https://www.kickstarter.com/projects/36162341/raspberry-pi-nixie-tube-driver


This repository contains the python library that was created from reading the
pins on the PCB. The library should be usable in the following manner:

```python
import raspberrypinixie

try:
    raspberrypinixie.setup()

    # Turn all LED on
    raspberrypinixie.led_set(True, True, True, True ,True ,True)

    # Set Nixie tubes
    raspberrypinixie.nixie_set(1, 2, 3, 4 ,5 ,6)
finally:
    raspberrypinixie.cleanup(clear_led=False, clear_nixie=False)
```

This repository also contains a couple of sample programs using the library
as follows:

Auto test program
------------------------------------------------------------------------------

To run the Auto test program, execute the following:

```bash
# The library module can be executed to start the Auto test program:
sudo python raspberrypinixie.py

# The Auto test program has various options:
sudo python raspberrypinixie.py --delay 0.1 --nixie-off-test --led-mode ON

# To see additional options:
python raspberrypinixie.py --help
```

Basic clock program
------------------------------------------------------------------------------

The clock program is a 24 hour clock that uses all Nixie tubes as digits and
has options on whether to strobe the LED, keep them all ON or all OFF.

```bash
# To run the clock program:
sudo python samples/clock.py

# To see clock program options:
python samples/clock.py --help

# Run the clock program with UTC time offset and an always on LED
sudo python samples/clock.py --hour-offset -7 --led-mode ON
```

Weather clock program
------------------------------------------------------------------------------

The Weather clock program uses the first 2 Nixie tube as the temperature at
the specified location. The first LED will be on when the temperature is less
than 0 and the second LED will be on when the temperature is greater than 99.

__Note:__ The Weather clock program will connect to MetaWeather.com to get the 
temperature, and requires Python3 for https TLS 1.2 support 

```bash
# To run the weather clock program:
sudo python3 samples/weather-clock.py "San%20Francisco"

# Display the temperature in Fahrenheit and UTC time offset:
sudo python3 samples/weather-clock.py "San%20Francisco" --fahrenheit --hour-offset -7
```

Direct LED and Nixie controller
------------------------------------------------------------------------------

The LED set and Nixie set program directly sets the LED or Nixie tubes
respectively. They will turn off any LEDs or Nixie tubes not specified in the
execution.
```bash
# Turn on LED1, LED3 and LED6
sudo python samples/led_set.py --led1 --led3 --led6

# Set Nixie tube 2 to 1, Nixie tube 4 to 2, and Nixie tube 5 to 3
sudo python samples/nixie_set.py --nixie2=1 --nixie4=2 --nixie5=3

# Turn all LED off
sudo python samples/led_set.py

# Turn all Nixie tube off
sudo python samples/nixie_set.py
```