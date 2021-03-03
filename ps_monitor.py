import asyncio
import subprocess
import ws_server

async def start_ps_monitor(sm):
    logger.info("Starting ps monitor as an infinite loop")
    while True:
        logger.info("Looping ps monitor")
        ps = subprocess.getoutput('./pffmpeggrep.sh').split()
        if ps:
            ws_server.send_message("zero process running")
        else:
            ws_server.send_message("zero process not running")
        asyncio.sleep(5)
    
