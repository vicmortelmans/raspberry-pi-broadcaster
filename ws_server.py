import asyncio
from aiohttp import web
import aiohttp
import aiohttp_jinja2
import jinja2
import json
import logging
import os

import default_form_data
import state

logger = logging.getLogger('websockets')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

connected_websockets = set()

async def socket_handler(request):
    logger.info("New client connected")

    ws = web.WebSocketResponse()
    #ws = web.WebSocketResponse(heartbeat=5.0)
    await ws.prepare(request)

    # Register
    connected_websockets.add(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                message = msg.data.strip()
                logger.info("Receiving message: " + message)
                if message == '__ping__':
                    # answer ping
                    answer = message
                else:
                    # convert json string to dict and pass along to state machine
                    answer = state.Machine().on_event(json.loads(message))
                # on_event() can use send_message() to send messages to all clients,
                # but if a reply is made to the sending client only, the answer is used
                if answer:
                    await ws.send_str(answer)
                    logger.info("Answered message: " + answer)
            except KeyError as e:
                logger.error("Message parsing error: ", exc_info=e)
                # Ignoring message
            except json.decoder.JSONDecodeError as e:
                logger.error("Message is not valid json: ", exc_info=e)
                # Ignoring message

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error('Socket connection closed with exception %s' % ws.exception())
            break

        elif msg.type == aiohttp.WSMsgType.CLOSED:
            logger.info('Socket connection closed')
            break

        else:
            logger.error("Unknown websocket message type")
            break

    # Unregister
    logger.info("Client has disconnected")
    connected_websockets.remove(ws)

    return ws

async def site_handler(request):
    context = {
        'state': state.Machine().state_string()
    }
    context.update(default_form_data.defaults)
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
    app.router.add_static('/site/img/', path='img', name='img')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logger.info("Starting server as a task [ok]")


async def send_message(message):
    global connected_websockets

    logger.info(f"Going to send message '{message}' to all connected clients")

    for ws in connected_websockets:
        logger.info(f"Sending message...")
        try:
            await ws.send_str(message)
        except ConnectionResetError as e:
            logger.error(f"Socket closed: '{e}'")

