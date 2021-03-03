import asyncio
import websockets
import logging

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

connected = set()

async def client_handler(websocket, path):
    global state_machine

    logger.info("New client connected")
    # Register.
    connected.add(websocket)
    try:
        async for message in websocket:
            logger.info("Receiving message: " + message.strip())
            state_machine.on_event(message.strip())
    finally:
        # Unregister.
        connected.remove(websocket)
        logger.info("Client has disconnected")

async def start_server(sm):
    """Start the server."""
    global state_machine
    state_machine = sm

    logger.info("Starting server as a task")
    server = await websockets.serve(client_handler, "localhost", 8080)
    logger.info("Starting server as a task [ok]")
    
async def send_message(message):
    global connected

    logger.info(f"Going to send message '{message}'")

    for websocket in connected:
        await websocket.send(message)
