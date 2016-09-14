"""New TRTL algorithm."""
from header import *  # NOQA
import boardless_tracker as track
import time
from math import sqrt
# import threading


def float_check(tracker):
    """Update various status variables (drifting and float checks)."""
    is_float_coords = (type(tracker.get_lat()) is float and
                       type(tracker.get_lon()) is float)
    is_float_yaw = type(tracker.get_yaw()) is float

    return is_float_coords, is_float_yaw

def error(predicted, actual):
    """Return the error from the calculated and actual bearing."""
    return min(abs(predicted - actual), abs(predicted - (360 + actual)))

def run():
    """Main algorithmic loop."""
    tracker = track.Tracker('COM2', 1.1, 115200)
    errors = []
    init_dist_threshold = 5
    dist_threshold = 3  # Threshold for linear movement in meters
    rotate_threshold = 4  # Threshold for rotational movement in degrees
    coords, calc_bearings, comp_bearings = initialize(tracker,
                                                      init_dist_threshold)

    filename = (time.strftime("%d/%m/%Y").replace("/", "-") + "_" +
                tracker.get_time().replace(":", "-") + '.txt')
    with open(filename, 'w') as data:
        # self.raw_data = open("raw_" + filename, 'w')
        try:
            while True:

                tracker.refresh()
                print(tracker.get_time())
                state = ""
                is_float_coords, is_float_yaw = float_check(tracker)

                if tracker.is_fixed():
                    print("Fixed")

                    if is_float_coords:
                        coords.add_coords(tracker.get_lat(), tracker.get_lon())

                    if is_float_yaw:
                        comp_bearings.add_bearing(tracker.get_yaw())

                    drifting = drift_check(coords, calc_bearings, comp_bearings,
                                           rotate_threshold)

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

                        data.write(str(tracker.get_time()) + ', ' +
                                   str(coords.lats[0]).rjust(20) + ', ' +
                                   str(coords.longs[0]).rjust(20) + ', ' +
                                   str(comp_bearings.b[0]).rjust(20) + ', ' +
                                   str(calc_bearings.b[0]).rjust(20) + ', ' +
                                   str(tracker.get_true()).rjust(20) + ', ' +
                                   state + '\n')
                        # self.raw_data.write(str(tracker.get_time()) + ', ' +
                        #                     str(tracker.get_lat()) + '\n')

                        errors.append(error(calc_bearings.b[0], tracker.get_true()))
                        square_errors = [x ** 2 for x in errors]
                        rms_error = sqrt(sum(square_errors)/len(square_errors))
                    except (Exception):
                        print("RMS:", rms_error)
                        return rms_error
                else:
                    print('No fix')
                    coord, calc_bearings, comp_bearings = initialize(tracker, init_dist_threshold)
        except IndexError:
            print("RMS:", rms_error)
            return rms_error

run()
