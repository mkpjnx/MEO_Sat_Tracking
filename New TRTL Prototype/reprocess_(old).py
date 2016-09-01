"""Read in data from a text file and process it using the algorithm.

Current output line format:
TIME, LAT, LON, CALC_BEARING, HEADING, STATUS

"""
# import tracker as track
import header


class Transcriber:
    """docstring for Transcriber."""

    def __init__(self, filename):
        """Constructor."""
        self.filename = filename
        self.data = []
        self.index = 0
        self.generate_data()
        print("Data populated, max index", self.max_index)

    def generate_data(self):
        """Read a line and extract the variables."""
        with open(self.filename) as f:
            for line in f:
                data_list = line.replace('\n', '').split(',')
                try:
                    self.data.append((data_list[0], data_list[1], data_list[2],
                                      data_list[4]))
                except IndexError:
                    print("Ignoring malformed sentence at", line)
        self.max_index = len(self.data) - 1

    def refresh(self):
        """Emulate refreshing the tracker by advancing to the next dataset."""
        if self.index < self.max_index:
            self.index += 1
        print("Refreshed. New index", self.index)

    def get_time(self):
        """Return time."""
        # print("Time", self.data[self.index][0])
        return self.data[self.index][0]

    def get_lat(self):
        """Return latitude."""
        # print("Lat", self.data[self.index][1])
        try:
            lat = float(self.data[self.index][1])
        except TypeError:
            print("TypeError encountered", self.data[self.index][1])
            lat = 0
        finally:
            return lat

    def get_lon(self):
        """Return longitude."""
        # print("Lon", self.data[self.index][2])
        try:
            lon = float(self.data[self.index][2])
        except TypeError:
            print("TypeError encountered", self.data[self.index][2])
            lon = 0
        finally:
            return lon

    def get_yaw(self):
        """Return heading."""
        # print("Yaw", self.data[self.index][3])
        try:
            yaw = float(self.data[self.index][3])
        except TypeError:
            print("TypeError encountered", self.data[self.index][3])
            yaw = 0
        finally:
            return yaw


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


def update_status(tracker, coords, calc_bearings, comp_bearings,
                  rotate_threshold):
    """Update various status variables (drifting and float checks)."""
    # drifting = drift_check(coords, calc_bearings, comp_bearings,
    #                        rotate_threshold)
    is_float_coords = (type(tracker.get_lat()) is float and
                       type(tracker.get_lon()) is float)
    is_float_yaw = type(tracker.get_yaw()) is float

    return is_float_coords, is_float_yaw


def initialize(tracker, dist_threshold):
    """Initilialize the tracker with the given thresholds."""
    coords = header.Coords(tracker.get_lat(), tracker.get_lon())
    # tracker.refresh()
    is_float_coords = (type(tracker.get_lat()) is float and
                       type(tracker.get_lon()) is float)

    for i in range(2):
        # print("I'm stuck! 1")
        if is_float_coords:
            coords.add_coords(tracker.get_lat(), tracker.get_lon())

    # while coords.get_dist_travelled() < dist_threshold:
    #     # print("I'm stuck! 2")
    #     coords.lock()
    #     tracker.refresh()
    #
    #     if is_float_coords:
    #         coords.add_coords(tracker.get_lat(), tracker.get_lon())

    calc_bearings = header.Bearings(coords.get_current_bearing())
    comp_bearings = header.Bearings(tracker.get_yaw())

    return coords, calc_bearings, comp_bearings


def run():
    """Main algorithmic loop."""
    tracker = Transcriber(file_in)
    init_dist_threshold = 2
    dist_threshold = 3  # Threshold for linear movement in meters
    rotate_threshold = 4  # Threshold for rotational movement in degrees
    coords, calc_bearings, comp_bearings = initialize(tracker,
                                                      init_dist_threshold)

    filename = (file_in.rsplit('.', 1)[0] + "_reprocessed.txt")
    print("Opening file", filename)
    data = open(filename, 'w')

    while tracker.index < tracker.max_index:
        # print("I'm stuck! 3")
        tracker.refresh()
        print(tracker.get_time())
        state = ""

        is_float_coords, is_float_yaw = update_status(
            tracker, coords, calc_bearings, comp_bearings, rotate_threshold)
        try:
            drifting = drift_check(coords, calc_bearings, comp_bearings,
                                   rotate_threshold)
        except IndexError:
            print("Drift check failed!")

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

            data.write(str(tracker.get_time()) + ', ' +
                       str(coords.lats[0]) + ', ' +
                       str(coords.longs[0]) + ', ' +
                       str(calc_bearings.b[0]) + ', ' +
                       str(comp_bearings.b[0]) + ', ' +
                       state + '\n')
        except (TypeError):
            pass
    data.close()

file_in = "2016-08-04_18-11-10.000.txt"
run()
