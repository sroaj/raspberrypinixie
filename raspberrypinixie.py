# -*- coding: utf-8 -*-
"""
Raspberry Pi Nixie tube driver library for the following Kickstarter project:
https://www.kickstarter.com/projects/36162341/raspberry-pi-nixie-tube-driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Allows independent control of Nixie Tube and LED on the board.

Example:
        >>> import raspberrypinixie
        >>> raspberrypinixie.setup()

        >>> raspberrypinixie.led_set(True, True, True, True ,True ,True)
        >>> raspberrypinixie.nixie_set(1, 2, 3, 4 ,5 ,6)

Make sure to call cleanup before the program exit to release the GPIO pins.

Example:

        >>> raspberrypinixie.cleanup()

Values can also be specified as None or default, in which case the Nixie tube
will be turned off. LEDs can also be turned off in the same manner.

Example:

        >>> raspberrypinixie.nixie_set(4, None, 9, None ,1 ,7)
        >>> raspberrypinixie.nixie_set(nixie1=4, nixie3=9, nixie5=1, nixie6=7)

        >>> raspberrypinixie.led_set(True, False, True, False, True, True)
        >>> raspberrypinixie.led_set(led1=True, led3=True,
                                     led5=True, led6=True)

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import time
import itertools
import logging
from RPi import GPIO

__title__ = 'raspberrypinixie'
__version__ = '1.0.0'
__author__ = 'Sroaj Sosothikul'
__all__ = ["setup", "cleanup", "led_set", "nixie_set"]

PULSE_WIDTH_SEC = 1.0 / 10000.0

LED_SER = 15
LED_nOE = 18
LED_RCLK = 19
LED_SRCLK = 16

LED_OUTPUTS_PINS = [LED_SER, LED_nOE, LED_RCLK, LED_SRCLK]

NIXIE_SER = 11
NIXIE_nOE = 13
NIXIE_RCLK = 8
NIXIE_SRCLK = 12

NIXIE_OUTPUT_PINS = [NIXIE_SER, NIXIE_nOE, NIXIE_RCLK, NIXIE_SRCLK]

logger = logging.getLogger("raspberrypinixie")


def _pin_pulse(pin, initial_state=GPIO.LOW, pulse_width=PULSE_WIDTH_SEC):
    # type: (int, bool, Union[int, float]) -> None
    """Sends one pulse to the specified pin.

    The pin will be returned to the specified initial state after the pulse

    Args:
        pin: The pin to pulse.
        initial_state: The negation of this will be used as the pulse.
            Defaults to GPIO.LOW.
        pulse_width: how long, in seconds, to pulse the pin.
            Defaults to PULSE_WIDTH_SEC.
    """
    GPIO.output(pin, not initial_state)
    try:
        time.sleep(pulse_width)
    finally:
        GPIO.output(pin, initial_state)


def _load_shift_register(ser_pin, srclk_pin, rclk_pin, binary_inputs):
    # type: (int, int, int, Iterable[bool]) -> None
    """Loads a shift register from a binary list.

    This assumes that the shift register is ready to accept inputs (clear pin
    is not asserted).

    Remember that the first value loaded into a shift register is shifted to
    become the last value in the register.

    Args:
        ser_pin: The pin to use for binary data output.
        srclk_pin: The pin to use as clock for binary data.
        rclk_pin: The pin to use to trigger the output of data.
        binary_inputs: The values to load the shift register
    """
    if logger.isEnabledFor(logging.DEBUG):
        # The binary_inputs may be a generator, so save all the binary_inputs
        # into a list so they can be iterated over more than once.
        binary_inputs = list(binary_inputs)
        logger.debug("Loading shift register using pins (SER: %s, SRCLK: %s, "
                     "RCLK: %s) with the following values: %s",
                     ser_pin, srclk_pin, rclk_pin, binary_inputs)

    # Use each element in the list as binary data output
    for output_bit in binary_inputs:
        GPIO.output(ser_pin, output_bit)
        _pin_pulse(srclk_pin)

    # Data has been loaded, trigger the output of data
    _pin_pulse(rclk_pin)
    # This is not in a try finally so that partially loaded data is never
    # displayed


def _int_to_bcd(value):
    # type: (Optional[int]) -> Tuple[bool, bool, bool, bool]
    """Converts an integer to a tuple representing the input bits to a BCD.

    If the input value is None, an all high output will be produced. This will
    typically make the BCD to turn its corresponding output off.

    Args:
        value: The value to be converted.

    Returns:
        tuple of bool corresponding to the BCD representation of the
        inputted value.
    """
    if value is None:
        output = (GPIO.HIGH,) * 4
    elif 0 <= value <= 9:
        output = tuple(int(digit, 2) for digit in "{:04b}".format(value))
        assert len(output) == 4
    else:
        raise ValueError("Specified input must be either None or between "
                         "0 and 9. Input was: {!r}.".format(value))
    logger.debug("Converted %s to %s", value, output)
    return output


def _led_enable():
    # type: () -> None
    """Turns all LED off without clearing state.

    This operation does not require a clock, so is faster than modifying each
    register one by one.
    """
    GPIO.output(LED_nOE, GPIO.LOW)


def _led_disable():
    # type: () -> None
    """Turns all LED on with the current state.

    This operation does not require a clock, so is faster than modifying each
    register one by one.
    """
    GPIO.output(LED_nOE, GPIO.HIGH)


def led_set(led1=False,  # type: bool
            led2=False,  # type: bool
            led3=False,  # type: bool
            led4=False,  # type: bool
            led5=False,  # type: bool
            led6=False,  # type: bool
            ):
    # type: (...) -> None
    """Sets the LED to the user specified states.

    If any LED is not specified, it will be turned off as if it was specified
    with a value of False.

    Args:
        led1: State to set LED1. Defaults to False.
        led2: State to set LED2. Defaults to False.
        led3: State to set LED3. Defaults to False.
        led4: State to set LED4. Defaults to False.
        led5: State to set LED5. Defaults to False.
        led6: State to set LED6. Defaults to False.
    """
    led_states = (led1, led2, led3, led4, led5, led6)
    logger.info("Setting LED states: %s", led_states)

    # Reverse the input order. This is because the first value loaded into a
    # shift register is shifted to become the last value in the register. And
    # the shift register on this PCB is hooked up so that the first register
    # is displayed leftmost.
    _load_shift_register(LED_SER, LED_SRCLK, LED_RCLK, reversed(led_states))


def _nixie_enable():
    # type: () -> None
    """Turns all Nixie tubes off without clearing state

    This operation does not require a clock, so is faster than modifying each
    register one by one.
    """
    GPIO.output(NIXIE_nOE, GPIO.LOW)


def _nixie_disable():
    # type: () -> None
    """Turns all Nixie tubes on with the current state.

    This operation does not require a clock, so is faster than modifying each
    register one by one.
    """
    GPIO.output(NIXIE_nOE, GPIO.HIGH)


def nixie_set(nixie1=None,  # type: Optional[int]
              nixie2=None,  # type: Optional[int]
              nixie3=None,  # type: Optional[int]
              nixie4=None,  # type: Optional[int]
              nixie5=None,  # type: Optional[int]
              nixie6=None,  # type: Optional[int]
              ):
    # type: (...) -> None
    """Sets the Nixie tubes to the user specified values.

    Specifying a value of None will turn off that Nixie tube.

    If any Nixie tube is not specified, it will be turned off as if it was
    specified with a value of None.

    Args:
        nixie1: Value to set Nixie tube 1. Defaults to None.
        nixie2: Value to set Nixie tube 2. Defaults to None.
        nixie3: Value to set Nixie tube 3. Defaults to None.
        nixie4: Value to set Nixie tube 4. Defaults to None.
        nixie5: Value to set Nixie tube 5. Defaults to None.
        nixie6: Value to set Nixie tube 6. Defaults to None.
    """
    nixie_digits = (nixie1, nixie2, nixie3, nixie4, nixie5, nixie6)
    logger.info("Setting Nixie values: %s", nixie_digits)

    # Reverse the input order. This is because the first value loaded into a
    # shift register is shifted to become the last value in the register. And
    # the shift register on this PCB is hooked up so that the first register
    # is displayed leftmost.
    reversed_nixie_digits = reversed(nixie_digits)

    # Convert the inputs numbers to their BCD representation. This will raise
    # if the user specified values out of the valid range of None and 0 to 9.
    list_of_bcd_inputs = [_int_to_bcd(nixie_digit) for nixie_digit in
                          reversed_nixie_digits]  # raises ValueError

    # Flatten the list of 4 boolean list into inputs for the shift register
    shift_register_inputs = itertools.chain.from_iterable(list_of_bcd_inputs)

    _load_shift_register(NIXIE_SER, NIXIE_SRCLK, NIXIE_RCLK,
                         shift_register_inputs)


def setup(clear_led=True, clear_nixie=True):
    # type: (bool, bool) -> None
    """Setup the Raspberry Pi GPIO channels and clear Nixie tubes or LEDs.

    By default this will clear both Nixie tubes and LEDs. This is a good idea
    as before the board was initialized, the states and values could be
    anything.

    Args:
        clear_led: Clear the LEDs. Defaults to True.
        clear_nixie: Clear the Nixie tubes. Defaults to True.
    """
    # Setup GPIO outputs.
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_OUTPUTS_PINS + NIXIE_OUTPUT_PINS, GPIO.OUT,
               initial=GPIO.LOW)

    if clear_led:
        # Set all LED to default which is off.
        led_set()
        _led_enable()

    if clear_nixie:
        # Set all Nixie tubes to default which is off.
        nixie_set()
        _nixie_enable()


def cleanup(clear_led=True, clear_nixie=True):
    # type: (bool, bool) -> None
    """Reset the channels used by this program to INPUT.

    By default this will clear both Nixie tubes and LEDs.

    Args:
        clear_led: Clear the LEDs. Defaults to True.
        clear_nixie: Clear the Nixie tubes. Defaults to True.
    """
    try:
        if clear_nixie:
            # Quickly turn the Nixie tubes off before using more time to
            # clear the registers
            _nixie_disable()

        if clear_led:
            # Quickly turn the LEDs off before using more time to clear the
            # registers
            _led_disable()
            # Set all LED to default which is off.
            led_set()

        if clear_nixie:
            # Set all Nixie tubes to default which is off.
            nixie_set()

    finally:
        # Cleanup the GPIO pins that were initialized in setup.
        GPIO.cleanup(LED_OUTPUTS_PINS + NIXIE_OUTPUT_PINS)


if __name__ == "__main__":
    from collections import deque
    import argparse
    parser = argparse.ArgumentParser(
        description="Walks the Nixie tubes digits from 0 to 9 and various LED "
        "configurations. This is an example program using the library "
        "included in this file.")
    parser.add_argument("--led-mode", choices=["STROBE", "ON", "OFF"],
                        default="STROBE", help="DEFAULT: STROBE. STROBE will "
                        "blank one LED every 11 number displayed. ON turns on"
                        " all LED. OFF turns off all LED.")
    parser.add_argument("--delay", "-d", type=float, default=1,
                        help="How long to wait until the next digit is "
                        "displayed.")
    parser.add_argument("--nixie-off-test", action="store_true")
    parser.add_argument("--verbose", "-v", action="count", default=0,
                        help="Change the logger level. Further increase "
                        "verbosity by repeating this option.")
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

    # This is the sequence of number to walk. Nixie tubes support digits from
    # 0 to 9.
    numbers = list(range(10))  # type: List[Union[int, None]]

    # If user requested, insert a None into the sequence as that's what we use
    # to turn a tube off.
    if args.nixie_off_test:
        numbers.append(None)

    # These are used to store the current numbers and led states being
    # displayed. This allows the next refresh to have the previously displayed
    # numbers.
    led_states = deque(maxlen=6)  # type: Deque[bool]
    nixie_values = deque(maxlen=6)  # type: Deque[Union[int, None]]

    # Initialize all the LED as ON or OFF depending on user argument
    # OFF       -> all False
    # ON/STROBE -> all True
    led_states.extend([args.led_mode != "OFF"]*6)

    # Sets the Nixie tube to 4 5 6 7 8 9 as the next digit to be inserted
    # is 0.
    nixie_values.extend(range(4, 10))

    ##########################################################################

    print("Starting Auto test program. Interrupt to exit.")

    try:
        setup()  # may raise if GPIO pins are already in use.

        # Refresh the Nixie tubes and LED until an interrupt occurs.
        while True:
            # Add an additional blank item to the list of LED to blank so that
            # the last loop has all LED on.
            for led_to_blank in numbers + [-1]:
                for next_number_to_display in numbers:
                    nixie_set(*nixie_values)
                    led_set(*led_states)

                    time.sleep(args.delay)

                    nixie_values.append(next_number_to_display)
                    if args.led_mode == "STROBE":
                        led_states.append(
                            next_number_to_display != led_to_blank)

    except KeyboardInterrupt:
        print("Interrupted. Cleaning up and exiting.")
    finally:
        cleanup()
