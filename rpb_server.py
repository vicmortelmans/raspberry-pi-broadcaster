#!/usr/bin/python3
import asyncio
import RPi.GPIO as GPIO
import logging

import button_monitor
import camera
import led_driver
import ps_monitor
import state
import ws_server


async def start_services():
    logging.info('Entry')
    
    logging.info('Startup state machine')
    state.Machine()

    logging.info('Startup camera stream')
    camera_task = camera.start_stream_async()
    logging.info('Startup camera stream [ok]')

    logging.info('Startup websocket server')
    ws_server_task = ws_server.start_server_async()
    logging.info('Startup websocket server [ok]')

    logging.info('Startup ps monitor')
    ps_monitor_task = ps_monitor.start_ps_monitor_async()
    logging.info('Startup ps monitor [ok]')

    logging.info('Startup led driver')
    led_driver_task = led_driver.start_led_driver_async()
    logging.info('Startup led driver [ok]')

    logging.info('Startup button monitor')
    button_monitor_task = button_monitor.start_button_monitor_async()
    logging.info('Startup button monitor [ok]')

    await asyncio.gather(camera_task, ws_server_task, ps_monitor_task, led_driver_task, button_monitor_task)

    logging.info('Exit')

if __name__ == "__main__":

    try:

        # start the service by runing "./rpb_server.py"  

        logging.basicConfig(format='[RPB] %(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.DEBUG)

        logging.info('Entry')

        loop = asyncio.run(start_services())

        logging.info('Exit')

    #execute this code if CTRL + C is used to kill python script
    except KeyboardInterrupt:

        print("Bye!")

    #execute code inside this block as the program exits
    finally:

        GPIO.cleanup()
