#!/usr/bin/python3
import asyncio
import logging
import state
import ws_server
import ps_monitor

async def start_services():
    logging.info('Entry')
    
    logging.info('Startup state machine')
    state_machine = state.RPB_State_Machine()

    logging.info('Startup websocket server')
    await ws_server.start_server(state_machine)
    logging.info('Startup websocket server [ok]')

    logging.info('Startup ps monitor')
    ps_monitor_task = asyncio.create_task(ps_monitor.start_ps_monitor(state_machine))
    logging.info('Startup ps monitor [ok]')

    await asyncio.sleep(100)
    logging.info('Exit')

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=logging.DEBUG)

    logging.info('Entry')

    loop = asyncio.run(start_services())

    logging.info('Exit')

