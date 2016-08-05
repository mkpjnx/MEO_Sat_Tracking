"""New TRTL algorithm."""
from header import *  # NOQA
import tracker as track
import threading


class my_thread(threading.Thread):
    """Thread for running the algorithm while allowing keyboard input."""

    def __init__(self, value):
        """Constructor."""
        super().__init__()
        self.val = value

    def increment(self):
        """Increment the character via character code."""
        self.val = chr(ord(self.val) + 1)

    def update_status(tracker):
        """Update various status variables (drifting and float checks)."""
        drifting = drift_check(coords, calc_bearings, comp_bearings,
                               rotate_threshold)
        is_float_coords = (type(tracker.get_lat()) is float and
                           type(tracker.get_lon()) is float)
        is_float_yaw = type(tracker.get_yaw()) is float

        return drifting, is_float_coords, is_float_yaw

    def run(self):
        """Main algorithmic loop."""
        tracker = track.Tracker('COM3', 1.1, 115200)
        init_dist_threshold = 5
        dist_threshold = 2  # Threshold for linear movement in meters
        rotate_threshold = 5  # Threshold for rotational movement in degrees
        coords, calc_bearings, comp_bearings = initialize(tracker,
                                                          init_dist_threshold)

        keyboard = self.val
        filename = (tracker.get_date().replace("/", "-") + "_" +
                    tracker.get_time().replace(":", "-") + '.txt')
        self.data = open(filename, 'w')
        self.raw_data = open("raw_" + filename, 'w')
        while True:

            tracker.refresh()
            print(tracker.get_time())
            state = ""
            drifting, is_float_coords, is_float_yaw = update_status(tracker)

            if tracker.is_fixed():
                print("Fixed")

                if is_float_coords:
                    coords.add_coords(tracker.get_lat(), tracker.get_lon())

                if is_float_yaw:
                    comp_bearings.add_bearing(tracker.get_yaw())

                if comp_bearings.delta_bearing() < rotate_threshold:
                    comp_bearings.lock()

                try:
                    if coords.get_dist_travelled() > dist_threshold:

                        if drifting:
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

                    self.data.write(str(tracker.get_time()) + ', ' +
                                    str(coords.lats[0]) + ', ' +
                                    str(coords.longs[0]) + ', ' +
                                    str(calc_bearings.b[0]) + ', ' +
                                    str(comp_bearings.b[0]) + ', ' +
                                    state + '\n')
                    self.raw_data.write(str(tracker.get_time()) + ', ' +
                                        str(tracker.get_lat()) + '\n')
                except (TypeError, SerialException):
                    pass
            else:
                print('No fix')
                coord, calc_bearings, comp_bearings = initialize(tracker, init_dist_threshold)

            if keyboard != self.val:
                print("Marking waypoint " + self.val)
                self.data.write(self.val + '\n')
                keyboard = self.val


def main():
    """Main function."""
    thread1 = my_thread('@')

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
