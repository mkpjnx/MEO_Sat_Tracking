import threading
import time

class myThread(threading.Thread):
    def __init__(self, value):
        threading.Thread.__init__(self)
        self.val = value

    def run(self):
        while True:
            time.sleep(1)
            #Replace this print line with your actual function, which can use self.val to say what the waypoint is
            print(self.val)

    def increment(self):
        self.val = chr(ord(self.val) + 1)

thread1 = myThread('A')

thread1.start()

while True:
    ii = input("Push enter to go to next subpoint")
    thread1.increment()
    pass