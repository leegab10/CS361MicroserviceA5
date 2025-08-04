import zmq
import time

print("🧪 Starting main.py test...")

context = zmq.Context()
socket = context.socket(zmq.REQ)

print("🔌 Connecting to timer service...")
socket.connect("tcp://localhost:5555")

time.sleep(1)
print("✅ Connected. Sending test command: start:1")
socket.send_string("start:1")

print("⏳ Waiting for reply...")
response = socket.recv_string()
print(f"✅ Received: {response}")

input("Press Enter to exit...")