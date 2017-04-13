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


import argparse
import raspberrypinixie


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sets the LED on the board via cmdline arguments")
    parser.add_argument("--led1", action="store_true", default=False)
    parser.add_argument("--led2", action="store_true", default=False)
    parser.add_argument("--led3", action="store_true", default=False)
    parser.add_argument("--led4", action="store_true", default=False)
    parser.add_argument("--led5", action="store_true", default=False)
    parser.add_argument("--led6", action="store_true", default=False)
    args = parser.parse_args()
    try:
        raspberrypinixie.setup(clear_led=False, clear_nixie=False)
        print("Setting LEDs to:\n{}".format(
            "\n".join(
                "{}={}".format(k, "ON" if v else "OFF")
                for k,v in sorted(args.__dict__.items()))))
        raspberrypinixie.led_set(
            led1=args.led1,
            led2=args.led2,
            led3=args.led3,
            led4=args.led4,
            led5=args.led5,
            led6=args.led6)
    finally:
        raspberrypinixie.cleanup(clear_led=False, clear_nixie=False)
