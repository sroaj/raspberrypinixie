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
        description="Sets the Nixie tubes on the board via cmdline arguments")
    parser.add_argument("--nixie1", type=int, default=None)
    parser.add_argument("--nixie2", type=int, default=None)
    parser.add_argument("--nixie3", type=int, default=None)
    parser.add_argument("--nixie4", type=int, default=None)
    parser.add_argument("--nixie5", type=int, default=None)
    parser.add_argument("--nixie6", type=int, default=None)
    args = parser.parse_args()
    try:
        raspberrypinixie.setup(clear_led=False, clear_nixie=False)
        print("Setting Nixie tubes to:\n{}".format(
            "\n".join(
                "{}={}".format(k, v if v is not None else "OFF")
                for k,v in sorted(args.__dict__.items()))))
        raspberrypinixie.nixie_set(
            nixie1=args.nixie1,
            nixie2=args.nixie2,
            nixie3=args.nixie3,
            nixie4=args.nixie4,
            nixie5=args.nixie5,
            nixie6=args.nixie6)
    finally:
        raspberrypinixie.cleanup(clear_led=False, clear_nixie=False)
