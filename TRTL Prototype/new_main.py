from header import *
import tracker as track
from time import sleep

def fix(tracker):
    while not tracker.is_fixed():
        tracker.refresh()
        print('Fixing')
        print(tracker.info)

def initialize(tracker, dist_threshold):
    fix(tracker)

    coords = Coords(tracker.get_lat(), tracker.get_lon())

    tracker.refresh()
    fix(tracker)
    while len(coords.lats) < 2:
        if type(tracker.get_lat()) is float and type(tracker.get_lon()) is float:
            coords.add_coords(tracker.get_lat(), tracker.get_lon())

    while coords.get_dist_travelled() < dist_threshold:
        coords.lock()
        tracker.refresh()
        
        if tracker.is_fixed():
            if type(tracker.get_lat()) is float and type(tracker.get_lon()) is float:
                coords.add_coords(tracker.get_lat(), tracker.get_lon())

        print('Initialize bearing')
        sleep(1)
    print('pass')
    calc_bearings = Bearings(coords.get_current_bearing())
    comp_bearings = Bearings(tracker.get_yaw())

    return coords, calc_bearings, comp_bearings

def drift_check(coords, calc_bearings, comp_bearings, rotate_threshold):
    return abs((coords.get_current_bearing() - calc_bearings.b[0]) - abs(comp_bearings.delta_bearing())) > rotate_threshold

def rotate_check(comp_bearings, rotate_threshold):
    return abs(comp_bearings.delta_bearing()) > rotate_threshold

def main():
    tracker = track.Tracker('COM3', 1.1, 115200)
    dist_threshold = 3 #Threshold for significant linear movement in meters
    rotate_threshold = 4 #Threshold for signicant rotational movement in degrees
    coords, calc_bearings, comp_bearings = initialize(tracker, dist_threshold)

    data = open('log.txt', 'w')
    try:
        while True:
            tracker.refresh()
            print(tracker.get_time())

            if tracker.is_fixed():
                print('Fixed')
                if type(tracker.get_lat()) is float and type(tracker.get_lon()) is float:
                    coords.add_coords(tracker.get_lat(), tracker.get_lon())

                if type(tracker.get_yaw()) is float:
                    comp_bearings.add_bearing(tracker.get_yaw())
                else:
                    comp_bearings.lock()
                try:
                    if coords.get_dist_travelled() > dist_threshold:

                        if drift_check(coords, calc_bearings, comp_bearings, rotate_threshold):
                            calc_bearings.adjust_bearing(comp_bearings.delta_bearing())

                        else:
                            calc_bearings.add_bearing(coords.get_current_bearing())
                except TypeError:
                    pass

                else:
                    #coords.lock()
                    if rotate_check(comp_bearings, rotate_threshold):
                        calc_bearings.adjust_bearing(comp_bearings.delta_bearing())

                    else:
                        calc_bearings.lock()


                data.write(str(tracker.get_time()) + ', ' + str(coords.lats[0]) + ', ' + str(coords.longs[0]) + ', ' + str(calc_bearings.b[0]) + '\n')

            else:
                print('No fix')
                coord, calc_bearings, comp_bearings = initialize(tracker, dist_threshold)

    except KeyboardInterrupt:
        pass

    data.close()

main()    
