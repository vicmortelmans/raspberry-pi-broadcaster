import asyncio
import logging
import state
import subprocess
import ws_server

async def start_ps_monitor_async():
    logging.info("Starting ps monitor as an infinite loop")
    sm = state.Machine()
    while True:
        logging.info("Looping ps monitor")
        if sm.has_state(state.StreamingState):
            logging.info("Testing ps")
            ps = subprocess.getoutput('./pffmpeggrep.sh').split()
            logging.info(ps)
        await asyncio.sleep(5)
    
