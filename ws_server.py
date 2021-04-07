import asyncio
from aiohttp import web
import aiohttp
import json
import logging
import state

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

connected = set()

async def client_handler(request):
    logger.info("New client connected")

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Register
    connected.add(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                logger.info("Receiving message: " + msg.data.strip())
                # convert json string to dict and pass along to state machine
                state.Machine().on_event(json.loads(msg.data.strip()))
            except KeyError as e:
                logger.error("Message parsing error: ", exc_info=e)
                # Ignoring message
            except json.decoder.JSONDecodeError as e:
                logger.error("Message is not valid json: ", exc_info=e)
                # Ignoring message

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    # Unregister
    logger.info("Client has disconnected")
    connected.remove(ws)

    return ws


async def start_server_async():
    """Start the server."""
    logger.info("Starting server as a task")
    app = web.Application()
    app.add_routes([web.get('/', client_handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logger.info("Starting server as a task [ok]")


async def send_message(message):
    global connected

    logger.info(f"Going to send message '{message}' to all connected clients")

    for ws in connected:
        await ws.send_str(message)
