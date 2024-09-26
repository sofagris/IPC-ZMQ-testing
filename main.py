# Description: This file contains the main application logic for the FastAPI
# application with WebSocket and ZeroMQ integration.
# Copyright: Copyright (c) 2024, Roy Michelsen
# License: MIT License

import asyncio
from contextlib import asynccontextmanager
import zmq
import zmq.asyncio
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

# Global counter for messages received
count = 0
# Lock to ensure thread-safe updates to the counter
count_lock = asyncio.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan function to handle startup and shutdown events.
    Initializes the set of WebSocket clients and starts the ZMQ server.
    """
    # Initialize the set for WebSocket clients
    app.state.websockets = set()
    # Start the ZMQ server and pass 'app' as a parameter
    zmq_task = asyncio.create_task(zmq_server(app))
    try:
        yield
    finally:
        # Cancel the ZMQ server task and wait for it to shutdown
        zmq_task.cancel()
        await zmq_task


# Create FastAPI application with lifespan
app = FastAPI(
    lifespan=lifespan,
    title="WebSocket and ZeroMQ Demo",
    description="Demo application for WebSocket and ZeroMQ integration",
    version="0.1.0"
)


async def zmq_server(app: FastAPI):
    """
    ZeroMQ server to receive messages from ZeroMQ clients.
    Upon receiving a message, it updates the counter and notifies
    WebSocket clients.
    """
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


async def notify_clients(app: FastAPI, message: str, count: int):
    """
    Notify all connected WebSocket clients with the new message and count.
    """
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
    """
    Root endpoint that returns a simple greeting.
    """
    return {"Hello": "World"}


@app.get("/count")
async def get_count():
    """
    Endpoint to get the current count of messages received.
    """
    async with count_lock:
        current_count = count
    return {"count": current_count}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint to allow clients to receive real-time updates.
    """
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
