
# WebSocket and ZeroMQ Demo

This is a demo application that integrates **FastAPI**, **WebSockets**, and **ZeroMQ** to showcase inter-process communication in Python. The application allows you to send messages from a ZeroMQ client to a FastAPI server, which then broadcasts the messages to all connected WebSocket clients in real-time.

## **Features**

- **ZeroMQ Server**: Receives messages from ZeroMQ clients.
- **WebSocket Endpoint**: Sends real-time updates to connected WebSocket clients.
- **Message Counter**: Keeps track of the number of messages received.
- **Thread-safe Operations**: Uses locks to ensure thread safety when updating shared data.

## **Requirements**

- Python 3.7 or higher
- Install dependencies using `pip`:

  ```bash
  pip install fastapi uvicorn pyzmq
  ```

## **How to Run the Application**

1. **Start the FastAPI Server**

   Run the following command to start the server:

   ```bash
   uvicorn main:app --reload
   ```

   - `main` refers to the Python file name (e.g., `main.py`).
   - The server will start on `http://127.0.0.1:8000`.

2. **Run a ZeroMQ Client**

   You can use the provided sample ZeroMQ client or create your own to send messages to the server.

   **Sample ZeroMQ Client:**

   ```python
   import zmq
   import zmq.asyncio
   import asyncio

   async def zmq_client():
       context = zmq.asyncio.Context()
       socket = context.socket(zmq.REQ)
       socket.connect("tcp://127.0.0.1:5555")

       for i in range(5):
           message = f"Hello {i}"
           await socket.send_string(message)
           reply = await socket.recv_string()
           print(f"Received reply: {reply}")
           await asyncio.sleep(1)

   if __name__ == "__main__":
       asyncio.run(zmq_client())
   ```
   - Run it using:

    ```bash
    python zmq-sender.py
    ```

3. **Connect a WebSocket Client**

   Use a WebSocket client to connect to the server and receive real-time updates.

   **Using `websocat` Command-Line Tool:**

   - Install `websocat` from [here](https://github.com/vi/websocat).

   - Run the following command:

     ```bash
     websocat ws://localhost:8000/ws
     ```

   **Using a Browser-Based WebSocket Client:**

   - You can use online tools like [WebSocket King](https://websocketking.com/) or browser extensions.
   - Connect to `ws://localhost:8000/ws`.

   **Using the supplied WebSocket-Client.py**

   - Simply start the client:

  ```bash
     python WebSocket-Client.py
  ```
  Remember to edit connection details in the file. 

## **API Endpoints**

- **GET /**

  - Description: Root endpoint that returns a simple greeting.
  - Example:

    ```bash
    curl http://127.0.0.1:8000/
    ```

- **GET /count**

  - Description: Returns the current count of messages received.
  - Example:

    ```bash
    curl http://127.0.0.1:8000/count
    ```

- **WebSocket /ws**

  - Description: WebSocket endpoint to receive real-time message updates.

## **Code Overview**

- **`lifespan` Function**

  - Manages application startup and shutdown.
  - Initializes WebSocket client storage and starts the ZeroMQ server.

- **`zmq_server` Function**

  - Listens for messages from ZeroMQ clients.
  - Updates the message counter and notifies WebSocket clients upon receiving a message.

- **`notify_clients` Function**

  - Sends messages to all connected WebSocket clients.
  - Handles exceptions and removes disconnected clients.

- **`websocket_endpoint` Function**

  - Handles WebSocket connections.
  - Maintains a set of active WebSocket clients.

## **Contributing**

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## **License**

This project is licensed under the MIT License.

## **Acknowledgments**

This project was developed with invaluable help from **ChatGPT** and **GitHub Copilot**. Their assistance in code generation and problem-solving was instrumental in bringing this project to fruition.

## **Additional Notes**

- **Thread Safety**: The `count` variable is protected by an asynchronous lock to ensure thread-safe increments when accessed by multiple coroutines.

- **ZeroMQ Context**: The `zmq.asyncio.Context()` is used for integrating ZeroMQ with the `asyncio` event loop.

- **Error Handling**: Exceptions during WebSocket communication are caught to prevent the server from crashing due to a single client error.

- **Extensibility**: This code serves as a foundation and can be extended to include more complex logic, authentication, or integration with other systems.
