from header import *
import tracker as track

def move_check(coord_list, lat, lon, threshold):
    
    if gps.distance_ll(coord_list.lats[0], coord_list.longs[0], lat, lon) > threshold:
        return True

    else:
        return False

def main():
    tracker = track.Tracker('COM3', 115200)
    dist_threshold = 5 #Threshold for significant linear movement in meters
    rotate_threshold = 5 #Threshold for significant rotational movement in degrees

    while not tracker.is_fixed():
        print("Fixing GPS")
        tracker.refresh()

    coord_list = Coords(tracker.get_lat(), tracker.get_lon())

    tracker.refresh()
    
    coord_list.add_coords(tracker.get_lat(), tracker.get_lon())
    calc_bear_list = Bearings(coord_list.get_current_bearing())
    comp_bear_list = Bearings(tracker.get_yaw())

    while True:
        tracker.refresh()
        print(tracker.get_time())
        print(tracker.unparsed)

        if tracker.is_fixed():
            current_lat = tracker.get_lat()
            current_lon = tracker.get_lon()

            if type(tracker.get_yaw()) is float:
                comp_bear_list.add_bearing(tracker.get_yaw())

            if move_check(coord_list, current_lat, current_lon, dist_threshold):

                if type(current_lat) is float:
                    coord_list.add_coords(current_lat, current_lon)

                current_rotation = coord_list.get_current_bearing() - calc_bear_list.b[0]

                if current_rotation > rotate_threshold:
                    if abs(current_rotation - calc_bear_list.delta_bearing()) < rotate_threshold:
                        calc_bear_list.add_bearing(coord_list.get_current_bearing())

            else:
                if comp_bear_list.delta_bearing() > rotate_threshold:
                    calc_bear_list.add_bearing((calc_bear_list.b[0] + comp_bear_list.delta_bearing()) % 360)

            print("Lat: ", coord_list.lats[0], " Long: ", coord_list.longs[0], sep = "")
            print("Bearing: ", calc_bear_list.b[0], " degrees E of N", sep = "")
            print("Distance travelled: ", coord_list.get_dist_travelled(), " meters")

        else:
            print("Fixing GPS")

        print('\n')

main()
            
