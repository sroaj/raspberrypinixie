#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import sys
# Configure paths so that you can run this without having to install
# raspberrypinixie as module
sys.path.insert(0,
               os.path.abspath(
                   os.path.join(os.path.dirname(__file__), '..')))  # NOQA

from datetime import datetime, timedelta
from collections import deque
import logging
import time
import argparse
import raspberrypinixie
import json

try:  # nocover
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:  # nocover
    from urllib2 import urlopen, URLError
    print("ERROR: You should use python3 as python2 urlopen is not able"
          " to connect to weather service over https TLS 1.2")
    sys.exit(1)


logger = logging.getLogger("raspberrypinixie")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Example Clock program")
    parser.add_argument('location',
                        help="Your location to which will be used to lookup"
                        " weather from metaweather location service "
                        "https://www.metaweather.com/api/#locationsearch")
    parser.add_argument("--led-mode", choices=["STROBE_LR", "STROBE_RL", "ON",
                                               "OFF"],
                        default="STROBE_LR", help="DEFAULT: STROBE_LR. STROBE"
                        " will move the led every 1 second Right to Left or "
                        "Left to Right. ON turns on all LED. OFF turns off "
                        "all LED.")
    parser.add_argument("--verbose", "-v", action="count", default=0,
                        help="Change the logger level. Further increase "
                        "verbosity by repeating this option.")
    parser.add_argument("--hour-offset", help="As there's no timezone support"
                        "in native python, this option allows basic clock "
                        "usage in your timezone", type=float, default=0.0)
    parser.add_argument("--fahrenheit", "-F", action="store_true",
                        help="Display temperature in Fahrenheit")
    args = parser.parse_args()

    ##########################################################################

    # Configure the logger.
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    # logging can only go as low as DEBUG which is specified by the user as
    # 2 verbose flags.
    logger.setLevel(max(
        logging.DEBUG,
        logger.getEffectiveLevel() - args.verbose * logging.DEBUG))

    led_states = deque(maxlen=4)  # type: Deque[bool]

    # Initialize all the LED as ON or OFF depending on user argument
    # OFF       -> all False
    # ON/STROBE -> all True
    led_states.extend([args.led_mode != "OFF"]*4)
    if "STROBE" in args.led_mode:
        led_states.append(False)

    ##########################################################################

    try:
        if args.location[0].isdigit() or args.location[0] == '-':
            url = "https://www.metaweather.com/api/location/search/"\
                  "?lattlong={}"
        else:
            url = "https://www.metaweather.com/api/location/search/?query={}"

        response = urlopen(url.format(args.location))
        locations = json.loads(response.read().decode("utf-8"))
        location = locations[0]
    except (IndexError, URLError):
        print("Location with name {!r} not found via "
              "https://www.metaweather.com/api/#locationsearch".format(
                  args.location))
        sys.exit(2)

    print("Will use the following location for weather: {!r} and unit: {}"
          .format(location["title"],
                  "Fahrenheit" if args.fahrenheit else "Celsius"))

    woeid = location["woeid"]

    ##########################################################################

    print("Starting Weather clock program using weather data from "
          "MetaWeather.com. Interrupt to exit.")
    try:
        raspberrypinixie.setup()
        while True:
            # MetaWeather asks us that we don't call their API too often
            response = urlopen(
                'https://www.metaweather.com/api/location/{}'.format(woeid))
            weather = json.loads(response.read().decode("utf-8"))
            current_temp_c = float(
                weather['consolidated_weather'][0]['the_temp'])

            if args.fahrenheit:
                converted_temp = int(9.0/5.0 * current_temp_c + 32)
            else:
                converted_temp = int(current_temp_c)

            # led1 is used to indicate negative temperatures
            # led2 is used to indicate temperature greater than 100
            led1 = False
            if converted_temp < 0:
                led1 = True
                converted_temp = -converted_temp
            led2 = False
            if converted_temp >= 100:
                led2 = True
                converted_temp -= 100

            # Update weather every 1 hour
            for i in range(3600):
                time_str = (datetime.now() +
                            timedelta(hours=args.hour_offset)
                            ).strftime("%H%M")


                combined_str = "{:02}{}".format(converted_temp, time_str)

                raspberrypinixie.nixie_set(*(int(i) for i in combined_str))
                raspberrypinixie.led_set(led1, led2, *led_states)

                time.sleep(1)
                if args.led_mode == "STROBE_LR":
                    led_states.appendleft(led_states.pop())
                elif args.led_mode == "STROBE_RL":
                    led_states.append(led_states.popleft())
    except KeyboardInterrupt:
        print("Interrupted. Cleaning up and exiting.")
    finally:
        raspberrypinixie.cleanup()
