from header import *
import tracker as track
from time import sleep
import threading

class myThread(threading.Thread):
    def __init__(self, value):
        threading.Thread.__init__(self)
        self.val = value

    def increment(self):
        self.val = chr(ord(self.val) + 1)

    def run(self):
        tracker = track.Tracker('COM3', 2, 115200)
        init_dist_threshold = 5
        dist_threshold = 2  # Threshold for significant linear movement in meters
        rotate_threshold = 3  # Threshold for signicant rotational movement in degrees
        coords, calc_bearings, comp_bearings = initialize(tracker, init_dist_threshold)

        kb = self.val
        self.data = open(tracker.get_date().replace("/", "-") + "_" + tracker.get_time().replace(":", "-") + '.txt', 'w')
        self.raw_data = open("raw_" + tracker.get_date().replace("/", "-") + "_" + tracker.get_time().replace(":", "-") + '.txt', 'w')

        while True:

            tracker.refresh()
            print(tracker.get_time())
            state = ""

            if tracker.is_fixed():
                print("Fixed")

                if type(tracker.get_lat()) is float and type(tracker.get_lon()) is float:
                    coords.add_coords(tracker.get_lat(), tracker.get_lon())

                if type(tracker.get_yaw()) is float:
                    comp_bearings.add_bearing(tracker.get_yaw())

                if comp_bearings.delta_bearing() < rotate_threshold:
                    comp_bearings.lock()

                try:
                    if coords.get_dist_travelled() > dist_threshold:

                        if drift_check(coords, calc_bearings, comp_bearings, rotate_threshold):
                            calc_bearings.adjust_bearing(comp_bearings.delta_bearing())
                            state = "D"

                        else:
                            calc_bearings.add_bearing(coords.get_current_bearing())
                            state = "N"

                    else:
                        coords.lock()

                        if rotate_check(comp_bearings, rotate_threshold):
                            calc_bearings.adjust_bearing(comp_bearings.delta_bearing())
                            state = "R"

                        else:
                            calc_bearings.lock()
                            state = "S"

                    self.data.write(str(tracker.get_time()) + ', ' + str(coords.lats[0]) + ', ' + str(coords.longs[0]) + ', ' + str(calc_bearings.b[0]) + ', ' + str(comp_bearings.b[0]) + ', ' + state + '\n')
                    self.raw_data.write(str(tracker.get_time()) + ', ' + str(tracker.get_lat()) + ', ' + str(tracker.get_lon()) + ', ' + str(tracker.get_yaw()) + '\n')

                except TypeError:
                    pass

            else:
                print('No fix')
                coord, calc_bearings, comp_bearings = initialize(tracker, init_dist_threshold)

            if kb != self.val:
                print("Marking waypoint " + self.val)
                self.data.write(self.val + '\n')
                kb = self.val

def main():
    thread1 = myThread('@')

    thread1.start()

    while True:
        ii = input("Push enter to go to next subpoint\n")
        if ii == "q":
            break
        thread1.increment()
        pass

    thread1.data.close()
    thread1.raw_data.close()

main()