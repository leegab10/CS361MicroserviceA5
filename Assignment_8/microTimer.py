import zmq
import time
import threading

# TimerService - this utilizes one countdown timer with support for the commands:
# start, pause, resume, cancel, and status check
class TimerMicroService:
    def __init__(self):
        self.reset()

    # to reset the timer (initialize or reset timer state)
    def reset(self):
        self.duration = 0 # total time in minutes
        self.start_time = None # when timer was started/restarted
        self.elapsed = 0 # time before pause
        self.running = False # is timer running?
        self.paused = False # is timer paused?
        self.calceled = False # is timer canceled?

    # start new timer for a given num of minutes
    def start(self, minutes):
        if self.running:
            return "Timer is currently running"
        self.duration = minutes * 60 # to get accurate time in min (not sec)
        self.elapsed = 0
        self.paused = False
        self.canceled = False
        self.running = True
        self.warned = False # reset the warning flag
        self.start_time = time.time()

        # timer runs in backround - so server is still responsive
        threading.Thread(target=self._run, daemon=True).start()
        return f"Timer started for {minutes} minutes."
    
    def _run(self):
        while self.elapsed < self.duration and not self.canceled:
            if not self.paused:
                time.sleep(0.1)
                self.elapsed = time.time() - self.start_time

                # for 5 min warning:
                time_left = self.duration - self.elapsed
                if not self.warned and time_left <= 300: # 5 min = 300sec
                    pub_socket.send_string("5 minutes left")
                    self.warned = True # this stops infinite loop after flag is set

        self.running = False
        # WHEN TIMER IS DONE SEND:
        if not self.canceled:
                pub_socket.send_string("Timer done!")
    
    # pause the timer if running
    def pause(self):
        # check for pause and already running
        if not self.running or self.paused:
            return "Can't pause. Timer is not running or already paused."
        self.elapsed = time.time() - self.start_time
        self.paused = True
        return "Timer paused."
    
    # resume timer
    def resume(self):
        # check for paused already
        if not self.paused:
            return "Timer is not paused"
        self.start_time = time.time() - self.elapsed # get how much time is left
        self.paused = False
        return "Timer resumed."
    
    #cancel timer
    def cancel(self):
        if not self.running:
            return "Timer is not running - can't cancel."
        self.canceled = True
        return "Timer canceled"
    
    def time_left(self):
        if not self.running:
            "Timer is not running"
        if self.paused:
            left = self.duration - self.elapsed # get time left if paused
        else:
            left = self.duration - (time.time() - self.start_time)

        return f"{max(0,left) / 60:.1f} minutes left." # divide for actual time to send




# ZeroMQ SETUP THINGS -------
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555") # use with port 5555 (run on same device)

pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:5556")  # new socket for publishing notifications (sending)

timer = TimerMicroService()
print("Timer microservice is running and waiting for commands (start:_m, pause, cancel, resume)")





while True:
    msg = socket.recv_string()

    try:
        #base case - start timer with 'start:'
        if msg.startswith("start:"):
            msgVal = msg[6:] # get everything after 'start:'
            minutes = int(msgVal[:-1]) if msgVal.endswith("m") else int(msgVal) # remove m if minutes
            res = timer.start(minutes) #response
        # pause timer
        elif msg == "pause":
            res = timer.pause()
        # cancel timer
        elif msg == "cancel":
            res = timer.cancel()
        # resume timer
        elif msg == "resume":
            res = timer.resume()
        # error (wrong command or incorrect input)
        else:
            res = "Unknown command."
    except Exception as e:
        res =  f"Error: {e}"

    socket.send_string(res) # always reply to commands