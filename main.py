# Instructions to Chat-GPT and Copilot:
# - All code comment in English, translate from Norwegian if needed
# - All code in English
# - Remember two lines between functions
# - Remember two lines between classes
# - Remember maximum 79 characters per line
# - FastAPI .on_event() is deprecated, use lifespan instead

import zmq                                  # Import ZeroMQ
import zmq.asyncio                          # Import ZeroMQ asyncio
import asyncio
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
# WebSocketDisconnect used to handle disconnection exceptions
from starlette.websockets import WebSocketDisconnect

count = 0
count_lock = asyncio.Lock()


# Define the lifespan function to handle startup and shutdown,
# as .on_event() is deprecated in FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the set for WebSocket clients
    app.state.websockets = set()
    # Staring the ZMQ server and sending 'app' as a parameter
    zmq_task = asyncio.create_task(zmq_server(app))
    try:
        yield
    finally:
        zmq_task.cancel()   # Cancel the ZMQ server task
        await zmq_task      # Wait for the ZMQ server to shutdown


# Create FastAPI application with lifespan
app = FastAPI(lifespan=lifespan)


# ZeroMQ server to receive messages from ZeroMQ client
async def zmq_server(app: FastAPI):
    global count
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://127.0.0.1:5555")

    while True:
        # Receive message from ZMQ client
        message = await socket.recv_string()
        # Update the counter in a thread-safe manner
        async with count_lock:
            count += 1
            current_count = count
        print(f"Message received: {message}")
        # Send response back to ZMQ client
        await socket.send_string(f"Messages received: {current_count}")
        # Notify all connected WebSocket clients
        await notify_clients(app, message, current_count)


async def notify_clients(
        app: FastAPI,
        message: str,
        count: int
        ):
    # Copy the set of WebSocket clients to avoid modification during iteration
    websockets = set(app.state.websockets)
    for ws in websockets:
        try:
            await ws.send_text(
                f"Messages received: {message}, sequence: {count}"
            )
        except Exception as e:
            print(f"Error sending message to client: {e}")
            # Remove the client if an error occurs
            app.state.websockets.remove(ws)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/count")
async def get_count():
    async with count_lock:
        current_count = count
    return {"count": current_count}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Add the WebSocket client to the set
    app.state.websockets.add(websocket)
    try:
        while True:
            # Keep the connection open
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    finally:
        # Remove the WebSocket client from the set upon disconnection
        app.state.websockets.remove(websocket)
