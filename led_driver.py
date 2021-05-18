import asyncio
import logging
import RPi.GPIO as GPIO
import time

import state


"""
The SIGNALS are defined by a frequency, duration tuple, in seconds.
The driver loop polls the state machine and runs at fairly high frequency, 
to support the 0.1s led frequency, and to be responsive to state changes.
"""

SIGNALS = {
    "IdleState": (4.0, 0.1),
    "StartingState": (0.2, 0.1),
    "StreamingState": (1.0, 1.0),
    "StoppingState": (0.2, 0.1),
    "RebootingState": (0.2, 0.1)
}

POLLING_FREQUENCY = 0.01  # frequency = 100/s (approx.)

"""
The LED is wired on GPIO6 (pin 31)
""" 

LED = 6


async def start_led_driver_async():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED, GPIO.OUT) 
    logging.info("Starting led driver as an infinite loop")
    sm = state.Machine()
    pp = False
    while True:
        statestring = sm.state_string()
        try:
            f,d = SIGNALS[statestring]
        except KeyError:
            logging.error(f"Unknown state: {statestring}")  # should not happen
            f,d = (1.0, 0.5)
        s = time.time()  # current time in seconds since whatever (floating number)
        p = s % f < d  # boolean for led on/off
        if p != pp: 
            pp = p  # remember previous position
            GPIO.output(LED, (GPIO.LOW, GPIO.HIGH)[p])  # using boolean as index on tuple
            logging.debug(("Led off", "Led on")[p])
        await asyncio.sleep(POLLING_FREQUENCY)
