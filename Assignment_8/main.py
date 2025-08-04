import zmq
import threading

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555") # timer service running on same device

# for listening to when timer is DONE:
sub = context.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")
sub.setsockopt_string(zmq.SUBSCRIBE, "")  # SUB-scribe to all messages that microTimer.py will PUB-lish

# background listener for when timer ends (otherwise no message is received)
def listen_for_notifications():
    while True:
        message = sub.recv_string()
        print(f"Notification: {message}\n> ")

threading.Thread(target=listen_for_notifications, daemon=True).start()

print("Timer Microservice Started!")
print("---------------------------")
print("commands:")
print(" start:10    -> Start 10 minute timer")
print(" pause       -> Pause timer")
print(" resume      -> Resume timer if paused")
print(" cancel      -> Cancel timer")
#print(" status      -> Time remaining")
print(" quit        -> Exit\n")

while True:
    try:
        command = input("> ").strip()
        if command == "quit":
            print("Exiting.")
            break
        socket.send_string(command)
        response = socket.recv_string()
        print(f"< {response}")
    except Exception as e:
        print(f"Error while communicating with timer microservice: {e}")
        break