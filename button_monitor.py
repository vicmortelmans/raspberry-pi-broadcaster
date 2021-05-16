import asyncio
import logging
import RPi.GPIO as GPIO

import state

POLLING_FREQUENCY = 0.01  # frequency = 1/0.01 s (approx.)


BUTTON = 21
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

async def start_button_monitor_async():
    logging.info("Starting button monitor as an infinite loop")
    import RPi.GPIO
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, bouncetime=50)
    down = 0  # last time the button was pressed down
    last = 0  # last time the button was released (s since whathever)
    last2 = 0  # 2nd last time ...
    while True:
        if not GPIO.event_detected(BUTTON):
            await asyncio.sleep(POLLING_FREQUENCY)
        else:
            logging.info("Button is pressed")
            down = time.time()
            while GPIO.input(21) == GPIO.LOW:
                await asyncio.sleep(POLLING_FREQUENCY)
            else:
                logging.info("Button is released")
                up = time.time()
                if up - down > 5.0:
                    # launch the event for starting/stopping
                    sm.on_event({'name': 'button-short'})
                elif up - last2 < 3.0:
                    # launch the event for rebooting
                    sm.on_event({'name': 'button-long'})
                else:
                    last2 = last
                    last = up
