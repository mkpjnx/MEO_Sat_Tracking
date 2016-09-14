"""Read in data from a text file and process it using the algorithm.

Current output line format:
TIME, LAT, LON, HEADING, TRUE_BEARING

"""
import header
from math import sqrt, floor


def error(predicted, actual):
    """Return the error from the calculated and actual bearing."""
    return min(abs(predicted - actual), abs(predicted - (360 + actual)))


class Reprocessor:
    """Docstring for Reprocessor."""

    def __init__(self, filename):
        """Constructor."""
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
        self.refresh()

    def refresh(self):
        """Read in new data from the file and split it."""
        # print("s#" + str(self.step), end=" ")
        self.info = self.lines[self.step].split(',')
        # print(self.info)
        if self.step < self.max_step:
            self.step += 1
        else:
            # print("Max exceeded")
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
        try:
            return float(self.info[3])
        except TypeError:
            print("Ignoring TypeError at", self.info)

    def get_true(self):
        """Get true bearing."""
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
        # print('Fixing')
        print(tracker.info)


# def drift_check(coords, calc_bearings, comp_bearings, rotate_threshold):
#     """Check if the vessel is currently drifting."""
#     # Check if the diff between the change in calculated bearing and the
#     # change in compass bearing are greater than an arbitrary threshold.
#     delta_diff = abs((coords.get_current_bearing() - calc_bearings.b[0]) -
#                      comp_bearings.delta_bearing())
#
#     return delta_diff > rotate_threshold


# def rotate_check(comp_bearings, rotate_threshold):
#     """Check if the vessel is currently rotating."""
#     return abs(comp_bearings.delta_bearing()) > rotate_threshold


def float_check(tracker):
    """Update various status variables (drifting and float checks)."""
    is_float_coords = (type(tracker.get_lat()) is float and
                       type(tracker.get_lon()) is float)
    is_float_yaw = type(tracker.get_yaw()) is float

    return is_float_coords, is_float_yaw


def main(idist, dist, rotate):
    """Run the algorithm."""
    tr = Reprocessor(filename)
    errors = []
    init_dist_threshold = idist
    dist_threshold = dist  # Threshold for sig. linear movement in meters
    rotate_threshold = rotate  # Threshold for sig. rotation in degrees
    coords, calc_bearings, comp_bearings = header.initialize(tr,
                                                             dist_threshold)
    version_string = ("_i" + str(init_dist_threshold) + "d" +
                      str(dist_threshold) + "r" + str(rotate_threshold))
    write_name = (filename.rsplit('.', 1)[0] + version_string +  # NOQA
                  "_reprocessed.txt")
    # with open(write_name, 'w') as data:
    # print("File opened:", write_name)
    try:
        while True:
            tr.refresh()
            state = ''
            if tr.is_fixed():
                # print('Fixed')
                # print("Step #", tr.step)
                # print(tr.get_time())
                (is_float_coords, is_float_yaw) = float_check(tr)

                if is_float_coords:
                    coords.add_coords(tr.get_lat(), tr.get_lon())

                if is_float_yaw:
                    comp_bearings.add_bearing(tr.get_yaw())
                else:
                    comp_bearings.lock()

                drifting = header.drift_check(coords, calc_bearings,
                                              comp_bearings, rotate_threshold)

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
                        if header.rotate_check(comp_bearings,
                                               rotate_threshold):
                            calc_bearings.adjust_bearing(
                              comp_bearings.delta_bearing())
                            state = "R"
                        else:
                            calc_bearings.lock()
                            state = "S"
                except TypeError:
                    print("TypeError")

                # data.write((str(tr.get_time()) + ', ' +
                #             str(coords.lats[0]).rjust(20) + ', ' +
                #             str(coords.longs[0]).rjust(20) + ', ' +
                #             str(comp_bearings.b[0]).rjust(20) + ', ' +
                #             str(calc_bearings.b[0]).rjust(20) + ', ' +
                #             str(tr.get_true()) + ', ' +
                #             state + '\n').rjust(20))

                errors.append(error(calc_bearings.b[0], tr.get_true()))
                square_errors = [x ** 2 for x in errors]
                rms_error = sqrt(sum(square_errors)/len(square_errors))

            else:
                # print('No fix')
                coord, calc_bearings, comp_bearings = header.initialize(
                  tr, dist_threshold)
    except IndexError:
        # print("Loop end reached.")
        return rms_error


filename = "testdata.txt"
trials = []
dist_step = .2
rotate_step = .2
prev_perc = 0
perc = 0
# Run the trials
with open("rms_list.txt", 'w') as rms:
    print("Working...")
    try:
        for i in range(int(50 / dist_step)):  # i = dist_threshold
            for j in range(int(90 / rotate_step)):  # j = rotate_threshold
                trial_data = (i * dist_step, j * rotate_step,
                              main(5, i * dist_step, j * rotate_step))
                trials.append(trial_data)
                rms.write(("{0:.2f}".format(trial_data[0]) + ", ").ljust(5) +
                          ("{0:.2f}".format(trial_data[1]) + ", ").ljust(5) +
                          ("{0:.2f}".format(trial_data[2]) + "\n").ljust(5))
                perc = floor(i/(50/dist_step)*100)
                if perc != prev_perc:
                    prev_perc = perc
                    print(str(perc) + "%")
                # print(("{0:.2f}".format(trial_data[0]) + ", ").ljust(5) +
                #       ("{0:.2f}".format(trial_data[1]) + ", ").ljust(5) +
                #       ("{0:.2f}".format(trial_data[2]).ljust(5)))
    except KeyboardInterrupt:
        print("Interrupted.")
    # Find the trial with the smallest error
    trial_errors = [item[2] for item in trials]
    min_error = min(trial_errors)
    min_index = trial_errors.index(min_error)
    min_trial = trials[min_index]

    min_dist, min_rot, min_rms = min_trial
    rms.write("Minimum trial:\nRMS: " + str(min_rms) + "\nDist: " +
              str(min_dist) + "Rot: " + str(min_rot))
    print("Minimum trial:\nRMS:", min_rms, "\nDist:", min_dist, "Rot:",
          min_rot)
