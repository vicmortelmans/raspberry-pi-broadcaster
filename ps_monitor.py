import asyncio
import logging
import subprocess
import ws_server

async def start_ps_monitor(sm):
    logging.info("Starting ps monitor as an infinite loop")
    while True:
        logging.info("Looping ps monitor")
        ps = subprocess.getoutput('./pffmpeggrep.sh').split()
        await asyncio.sleep(5)
    
