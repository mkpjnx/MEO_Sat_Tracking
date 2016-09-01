"""Read in data from a text file and process it using the algorithm.

Current output line format:
TIME, LAT, LON, CALC_BEARING, HEADING, STATUS

"""
import header
# import tracker as track
# from time import sleep


class Reprocessor:
    """Docstring for Reprocessor."""

    def __init__(self, filename):
        """Constructor."""
        self.filename = filename
        with open(filename, 'r') as f:
            print(f.name)
            self.lines = [line.rstrip('\n') for line in f]
            for item in self.lines:
                if item in "ABCDEFGHIJKLMNOPQRSTUVXYZ":
                    self.lines.remove(item)
        self.step = 0
        self.max_step = len(self.lines) - 1
        print("Max steps:", self.max_step)
        self.info = ""
        self.refresh()

    def refresh(self):
        """Read in new data from the file and split it."""
        print("s#" + str(self.step), end=" ")
        self.info = self.lines[self.step].split(',')
        if self.step < self.max_step:
            self.step += 1
        else:
            print("Max exceeded")
            raise IndexError

    def is_fixed(self):
        """Pretend the module is always fixed."""
        return True

    def get_lat(self):
        """Get lat."""
        try:
            return float(self.info[1])
        except TypeError:
            print("Ignoring TypeError at", self.info)

    def get_lon(self):
        """Get lon."""
        try:
            return float(self.info[2])
        except TypeError:
            print("Ignoring TypeError at", self.info)

    def get_yaw(self):
        """Get yaw."""
        return float(self.info[4])
        try:
            return float(self.info[4])
        except TypeError:
            print("Ignoring TypeError at", self.info)

    def get_time(self):
        """Get lon."""
        return self.info[0]


def fix(tracker):
    """Continuously attempt to get a fix on the tracker."""
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


def update_status(tracker, coords, calc_bear, comp_bear, rot_thres):
    """Update various status variables (drifting and float checks)."""
    drifting = drift_check(coords, calc_bear, comp_bear, rot_thres)
    is_float_coords = (type(tracker.get_lat()) is float and
                       type(tracker.get_lon()) is float)
    is_float_yaw = type(tracker.get_yaw()) is float

    return drifting, is_float_coords, is_float_yaw


def initialize(tracker, dist_threshold):
    """Initilialize the tracker with the given thresholds."""
    fix(tracker)

    coords = header.Coords(tracker.get_lat(), tracker.get_lon())

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
        # sleep(1)
    calc_bearings = header.Bearings(coords.get_current_bearing())
    comp_bearings = header.Bearings(tracker.get_yaw())

    comp_bearings.add_bearing(358.44)

    return coords, calc_bearings, comp_bearings


def main():
    """."""
    tr = Reprocessor(filename)
    init_dist_threshold = 5
    dist_threshold = 5  # Threshold for significant linear movement in meters
    rotate_threshold = 4  # Threshold for signicant rotation in degrees
    coords, calc_bearings, comp_bearings = initialize(tr, dist_threshold)
    versionstring = ("_i" + str(init_dist_threshold) + "d" +
                     str(dist_threshold) + "r" + str(rotate_threshold))
    writename = (filename.rsplit('.', 1)[0] + versionstring +
                 "_reprocessed.txt")
    with open(writename, 'w') as data:
        print("File opened:", writename)
        try:
            while True:
                tr.refresh()
                state = ''
                if tr.is_fixed():
                    # print('Fixed')
                    # print("Step #", tr.step)
                    # print(tr.get_time())
                    (drifting, is_float_coords, is_float_yaw) = update_status(
                      tr, coords, calc_bearings, comp_bearings,
                      rotate_threshold)

                    if is_float_coords:
                        coords.add_coords(tr.get_lat(), tr.get_lon())

                    if is_float_yaw:
                        comp_bearings.add_bearing(tr.get_yaw())

                    if comp_bearings.delta_bearing() < rotate_threshold:
                        comp_bearings.lock()

                    try:
                        if coords.get_dist_travelled() > dist_threshold:
                            if drifting:
                                calc_bearings.adjust_bearing(
                                  comp_bearings.delta_bearing())
                                state = "D"
                            else:
                                calc_bearings.add_bearing(
                                  coords.get_current_bearing())
                                state = "N"
                        else:
                            coords.lock()
                            if rotate_check(comp_bearings, rotate_threshold):
                                calc_bearings.adjust_bearing(
                                  comp_bearings.delta_bearing())
                                state = "R"
                            else:
                                calc_bearings.lock()
                                state = "S"
                    except TypeError:
                        print("TypeError")

                    data.write((str(tr.get_time()) + ', ' +
                                str(coords.lats[0]).rjust(20) + ', ' +
                                str(coords.longs[0]).rjust(20) + ', ' +
                                str(comp_bearings.b[0]).rjust(20) + ', ' +
                                str(calc_bearings.b[0]).rjust(20) + ', ' +
                                state + '\n').rjust(20))
                else:
                    print('No fix')
                    coord, calc_bearings, comp_bearings = initialize(
                      tr, dist_threshold)

        except IndexError:
            print("Loop end reached.")

filename = "2016-08-04_18-11-10.000.txt"
main()
