# Description: IPC sender using ZeroMQ
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5555")

message = "Hei fra kommandolinjeapplikasjonen"
socket.send_string(message)

reply = socket.recv_string()
print(f"Server svarte: {reply}")