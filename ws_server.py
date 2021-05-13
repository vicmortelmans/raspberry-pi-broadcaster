import asyncio
from aiohttp import web
import aiohttp
import aiohttp_jinja2
import jinja2
import json
import logging
import os
import socket
import state

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

connected_websockets = set()

async def socket_handler(request):
    logger.info("New client connected")

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Register
    connected_websockets.add(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                logger.info("Receiving message: " + msg.data.strip())
                # convert json string to dict and pass along to state machine
                answer = state.Machine().on_event(json.loads(msg.data.strip()))
                # on_event() can use send_message() to send messages to all clients,
                # but if a reply is made to the sending client only, the answer is used
                if answer:
                    await ws.send_str(answer)
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
    connected_websockets.remove(ws)

    return ws

async def site_handler(request):
    context = {
        'ip': get_ip()
    }
    response = aiohttp_jinja2.render_template("rpb_console.html", request, context=context)
    return response

async def start_server_async():
    """Start the server."""
    logger.info("Starting server as a task")
    app = web.Application()
    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.getcwd())
    )
    app.add_routes([web.get('/socket.io', socket_handler)])
    app.add_routes([web.get('/site/', site_handler)])
    app.router.add_static('/site/js/', path='js', name='js')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logger.info("Starting server as a task [ok]")


async def send_message(message):
    global connected_websockets

    logger.info(f"Going to send message '{message}' to all connected clients")

    for ws in connected_websockets:
        await ws.send_str(message)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    logger.info(f"My IP address is '{ip}'")
    s.close()
    return ip
