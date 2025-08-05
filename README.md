Timer Microservice

Description:
A Python microservice that manages a countdown timer using ZeroMQ.
The service is built using a multi-threaded design and communicates using two ZeroMQ patterns: REQ/REP for client-server commands and PUB/SUB for server-initiated notifications.

Prerequisites: 
Install Python Packages, The client must connect to localhost:5555 and localhost:5556 (the connections are listed below as they use ZeroMQ, The command must be in the following formats: 'start:5' (any number here works), 'cancel', 'resume', 'pause', 'exit'.

Connecting to localhosts for microTimer.py (contexts will be needed as well):
in the test/main.py file: 

Connection 1
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
^this is to receive a response to any of the commands above
Connection 2
sub = context.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")
sub.setsockopt_string(zmq.SUBSCRIBE, "")
^this is to constantly listen for 'timer is done' from the microservice

There will have to be a background listener to receive the data from the connection listed above - following an architecture similar to this below
while True:
        message = sub.recv_string()
        print(f"Notification: {message}\n> ")

It supports:
-Starting a timer in minutes 
-Pausing, resuming, canceling
-Notifications when 5 minutes remain and when the timer ends

This microservice follows a structured form of communication. The client sends commands to the server using REQ/REP. For example: `start:10` returns "Started for 10 minutes." or "Timer already running." 
The `pause`, `resume`, and `cancel` commands return their respective messages or errors. 
Invalid commands receive either an "Unknown command." or a detailed error message. 
The server uses PUB/SUB to send push notifications such as "5 minutes left" (when five minutes are left) and "Timer done!" (when the timer completes), without waiting for a request (hence use of SUB in addition to REQ)

