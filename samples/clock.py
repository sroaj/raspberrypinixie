#!/usr/bin/python
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


logger = logging.getLogger("raspberrypinixie")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Example Clock program")
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
    parser.add_argument("--date", help="Display the Year Month Day"
                        "instead of the time", action="store_const",
                        const="%y%m%d", dest="format", default='%H%M%S')
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

    led_states = deque(maxlen=6)  # type: Deque[bool]

    # Initialize all the LED as ON or OFF depending on user argument
    # OFF       -> all False
    # ON/STROBE -> all True
    led_states.extend([args.led_mode != "OFF"]*6)
    if "STROBE" in args.led_mode:
        led_states.append(False)

    ##########################################################################

    print("Starting Clock program. Interrupt to exit.")
    try:
        raspberrypinixie.setup()
        while True:
            time_str = (datetime.now() +
                        timedelta(hours=args.hour_offset)
                        ).strftime(args.format)

            raspberrypinixie.nixie_set(*(int(i) for i in time_str))
            raspberrypinixie.led_set(*led_states)

            time.sleep(1)
            if args.led_mode == "STROBE_LR":
                led_states.appendleft(led_states.pop())
            elif args.led_mode == "STROBE_RL":
                led_states.append(led_states.popleft())
    except KeyboardInterrupt:
        print("Interrupted. Cleaning up and exiting.")
    finally:
        raspberrypinixie.cleanup()
