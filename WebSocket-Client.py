# Description:
# Demo WebSocket client for receiving messages from the server
# TODO: Implement automatic reconnection and error handling

import websockets


# Connect to the server and listen for incoming messages
async def listen():
    uri = "ws://localhost:8001/ws"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            print(message)


# Start the WebSocket client
if __name__ == "__main__":
    import asyncio
    asyncio.run(listen())
