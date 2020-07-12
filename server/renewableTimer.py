from threading import Timer
import time

class RenewableTimer():

    
    def __init__(self):
        self.isActive = False
        self.timer = None
    
    def set_timer(self, timeout, callback):
        self.isActive = False
        self.timeout = timeout
        self.callback = callback
        self.timer = Timer(self.timeout, self.callback)

    def cancel(self):
        if self.timer:
            self.isActive = False
            self.timer.cancel()

    def start(self):
        self.isActive = True
        self.start_time = time.time()
        self.timer.start()

    def pause(self):
        if self.timer:
            self.isActive = False
            self.cancel_time = time.time()
            self.timer.cancel()
            return self.get_actual_time()

    def resume(self):
        if self.timer:
            self.isActive = True
            self.timeout = self.get_actual_time()
            self.timer = Timer(self.timeout, self.callback)
            self.start_time = time.time()
            self.timer.start()

    def get_actual_time (self):
        return self.timeout - (self.cancel_time - self.start_time)