from header import *  # NOQA
import tracker as track
from time import sleep


def fix(tracker):
    """Continously attempt to get a fix on the tracker."""
    while not tracker.is_fixed():
        tracker.refresh()
        print('Fixing')
        print(tracker.info)


def drift_check(coords, calc_bearings, comp_bearings, rotate_threshold):
    """Check if the vessel is currently drifting."""
    # Check if the difference between the change in calculated bearing and the
    # change in compass bearing are greater than an arbitrary threshold.
    delta_diff = abs((coords.get_current_bearing() - calc_bearings.b[0]) -
                     comp_bearings.delta_bearing())

    return delta_diff > rotate_threshold


def rotate_check(comp_bearings, rotate_threshold):
    """Check if the vessel is currently rotating."""
    return abs(comp_bearings.delta_bearing()) > rotate_threshold


def update_status(tracker):
    """Update various status variables (drifting and float checks)."""
    drifting = drift_check(coords, calc_bearings, comp_bearings,
                           rotate_threshold)
    is_float_coords = (type(tracker.get_lat()) is float and
                       type(tracker.get_lon()) is float)
    is_float_yaw = type(tracker.get_yaw()) is float

    return drifting, is_float_coords, is_float_yaw


def initialize(tracker, dist_threshold):
    """Initilialize the tracker with the given thresholds."""
    fix(tracker)

    coords = Coords(tracker.get_lat(), tracker.get_lon())

    tracker.refresh()
    fix(tracker)

    is_float_coords = (type(tracker.get_lat()) is float and
                       type(tracker.get_lon()) is float)
    while len(coords.lats) < 2:
        if is_float_coords:
            coords.add_coords(tracker.get_lat(), tracker.get_lon())

    while coords.get_dist_travelled() < dist_threshold:
        coords.lock()
        tracker.refresh()

        if tracker.is_fixed():
            if is_float_coords:
                coords.add_coords(tracker.get_lat(), tracker.get_lon())

        print('Initialize bearing')
        sleep(1)
    print('pass')
    calc_bearings = Bearings(coords.get_current_bearing())
    comp_bearings = Bearings(tracker.get_yaw())

    return coords, calc_bearings, comp_bearings

def main():
    """."""
    tracker = track.Tracker(input("Port: "), 115200, True)
    dist_threshold = 3  # Threshold for significant linear movement in meters
    rotate_threshold = 4  # Threshold for signicant rotation in degrees
    print('pass 1')
    coords, calc_bearings, comp_bearings = initialize(tracker, dist_threshold)
    print('pass 2')

    try:
        while True:
            tracker.refresh()
            print(tracker.get_time())

            if tracker.is_fixed():
                print('Fixed')

                (drifting, is_float_coords, is_float_yaw) = update_status()

                if is_float_coords:
                    coords.add_coords(tracker.get_lat(), tracker.get_lon())

                if is_float_yaw:
                    comp_bearings.add_bearing(tracker.get_yaw())
                else:
                    comp_bearings.lock()
                try:
                    # if coords.get_dist_travelled() > dist_threshold:
                        if drifting:
                            calc_bearings.adjust_bearing(
                                comp_bearings.delta_bearing())

                        else:
                            calc_bearings.add_bearing(
                                coords.get_current_bearing())
                except TypeError:
                    pass

                else:
                    # coords.lock()
                    if rotate_check(comp_bearings, rotate_threshold):
                        calc_bearings.adjust_bearing(
                            comp_bearings.delta_bearing())

                    else:
                        calc_bearings.lock()

                with open('log.txt', 'w') as data:
                    data.write(str(tracker.get_time()) + ', ' +
                               str(coords.lats[0]) + ', ' +
                               str(coords.longs[0]) + ', ' +
                               str(calc_bearings.b[0]) + '\n')

            else:
                print('No fix')
                coord, calc_bearings, comp_bearings = initialize(
                    tracker, dist_threshold)
    except KeyboardInterrupt:
        input("Loop interrupted")

main()
print("End of loop")
