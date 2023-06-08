import threading
from threading import Timer
import time
import queue
import random

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

q = queue.Queue()
global t
t = 0


def func():
    global t
    q.put(random.random())
    print(time.time() - t)
    t = time.time()


timer = RepeatTimer(0.001, func)
timer.start()

while True:
    t = time.time()
    time.sleep(5)
