import asyncio
import json
import logging
import websockets

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

connected = set()

async def client_handler(websocket, path):
    global state_machine

    logger.info("New client connected")
    # Register
    connected.add(websocket)
    # Keep listening for messages
    async for message in websocket:
        try:
            logger.info("Receiving message: " + message.strip())
            # convert json string to dict and pass along to state machine
            state_machine.on_event(json.loads(message.strip()))
        except KeyError as e:
            logger.error("Message parsing error: ", exc_info=e)
            # Ignoring message
        except json.decoder.JSONDecodeError as e:
            logger.error("Message is not valid json: ", exc_info=e)
            # Ignoring message
    # Unregister
    logger.info("Client has disconnected")
    connected.remove(websocket)

async def start_server(sm):
    """Start the server."""
    global state_machine
    state_machine = sm

    logger.info("Starting server as a task")
    server = await websockets.serve(client_handler, "localhost", 8080)
    logger.info("Starting server as a task [ok]")
    
async def send_message(message):
    global connected

    logger.info(f"Going to send message '{message}' to all connected clients")

    for websocket in connected:
        await websocket.send(message)
