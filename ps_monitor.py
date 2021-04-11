import asyncio
import logging
import state
import subprocess
import ws_server

pid = ''

async def start_ps_monitor_async():
    global pid
    logging.info("Starting ps monitor as an infinite loop")
    sm = state.Machine()
    while True:
        logging.info("Looping ps monitor")
        if sm.has_state(state.StreamingState):
            logging.info("Testing ps")
            ps = subprocess.getoutput('./pffmpeggrep.sh').split()
            logging.debug(ps)
            if not ps:
                sm.on_event({'name': 'streaming-died'})
            else:
                pid = ps[1]
        await asyncio.sleep(5)
    
