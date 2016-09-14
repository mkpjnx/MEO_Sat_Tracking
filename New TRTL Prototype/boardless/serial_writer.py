"""Emulate the arudino writing to the serial port."""
import serial
import time


class Writer:
    """."""

    def __init__(self, filename, port, timeout, baud=9600):
        """Constructor."""
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(5)
        self.filename = filename
        with open(filename, 'r') as f:
            # print(f.name)
            self.lines = [line.rstrip('\n') for line in f]
            for item in self.lines:
                if item in "ABCDEFGHIJKLMNOPQRSTUVXYZ":
                    self.lines.remove(item)
        self.step = 0
        self.max_step = len(self.lines) - 1
        # print("Max steps:", self.max_step)
        self.info = ""
        # self.refresh()

    def refresh(self):
        """Read in new data from the file and split it."""
        # print("s#" + str(self.step), end=" ")
        self.info = self.lines[self.step]
        # print(self.info)
        if self.step < self.max_step:
            self.step += 1
        else:
            # print("Max exceeded")
            raise IndexError
        self.ser.write((self.info + "\n").encode())
        print(self.info)

test = Writer("testdata.txt", 'COM1', 1.0, 115200)

while True:
    test.refresh()
    time.sleep(.1)
