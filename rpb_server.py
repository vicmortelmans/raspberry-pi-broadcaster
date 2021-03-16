#!/usr/bin/python3
import asyncio
import logging
import state
import ws_server
import ps_monitor

state_machine = None


async def start_services():
    global state_machine

    logging.info('Entry')
    
    logging.info('Startup state machine')
    state_machine = state.RPB_State_Machine()

    logging.info('Startup websocket server')
    ws_server_task = ws_server.start_server(state_machine)
    logging.info('Startup websocket server [ok]')

    logging.info('Startup ps monitor')
    ps_monitor_task = asyncio.create_task(ps_monitor.start_ps_monitor(state_machine))
    logging.info('Startup ps monitor [ok]')

    await asyncio.gather(ws_server_task, ps_monitor_task)

    logging.info('Exit')

if __name__ == "__main__":
    # start the service by runing "./rpb_server.py"  

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d %(funcName)s] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=logging.DEBUG)

    logging.info('Entry')

    loop = asyncio.run(start_services())

    logging.info('Exit')

