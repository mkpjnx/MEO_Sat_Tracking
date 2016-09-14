import math
import boardless_tracker as tracker
from time import sleep

class Bearings:
    """Object that stores bearing calculated from GPS position."""
    #This should not initialize with an initial bearing-I can explain later Ryan
    def __init__(self, bear = 0):
        """Constructor."""
        self.b = [bear]

    def add_bearing(self, b):
        """Insert a bearing at the beginning of the list."""
        self.b.insert(0, b)

        if len(self.b) >= 10:
            self.b.pop()

    # This stuff is for drift (maybe, we'll see how it goes)
    def delta_bearing(self):
        """Find the change in bearing."""
        return self.b[0]-self.b[1]

    def lock(self):
        self.add_bearing(self.b[0])

    def adjust_bearing(self, delta):
        self.add_bearing((self.b[0] + delta) % 360)

class Coords:
    """Object containing a set of the 10 most recent lat and long values in degrees."""
    def __init__(self, lat, lon):
        """Constructor"""
        self.lats = [lat]
        self.longs = [lon]

    def add_coords(self, lat, lon):
        """Add new coords to beginning of list and, if there are more than 10 coords, discard the oldest set."""
        self.lats.insert(0, lat)
        self.longs.insert(0, lon)

        if(len(self.lats) >= 10):
            __ = self.lats.pop()
            __ = self.longs.pop()

    def get_current_bearing(self):
        """Return most recent calculated bearing based on GPS coordinates
        In degrees East of North
        """

        #Find length of one degree of latitude and longitude based on average of two most recent latitudes
        latlen, lonlen = tracker.len_lat_lon((self.lats[0] + self.lats[1]) / 2)
        x = (self.longs[0] - self.longs[1]) * lonlen
        y = (self.lats[0] - self.lats[1]) * latlen

        b = 90 - math.degrees(math.atan2(y, x)) #Bearing in degrees East of North

        return b % 360

    def lock(self):
        self.lats[0] = self.lats[1]
        self.longs[0] = self.longs[1]

    def get_dist_travelled(self):
        """Return distance between two most recent points"""

        latlen, lonlen = tracker.len_lat_lon((self.lats[0] + self.lats[1]) / 2)
        x = (self.longs[0] - self.longs[1]) * lonlen
        y = (self.lats[0] - self.lats[1]) * latlen

        d = ((x * x) + (y * y)) ** .5
        return d


def fix(tracker):
    while not tracker.is_fixed():
        tracker.refresh()
        print('Fixing')


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
        # sleep(1)

    calc_bearings = Bearings(coords.get_current_bearing())
    comp_bearings = Bearings(tracker.get_yaw())

    return coords, calc_bearings, comp_bearings


def drift_check(coords, calc_bearings, comp_bearings, rotate_threshold):
    """Check if the vessel is currently drifting.

    Check if the difference between the change in calculated bearing and the
    change in compass bearing are greater than an arbitrary threshold.
    """
    delta_diff = abs((coords.get_current_bearing() - calc_bearings.b[0]) -
                     comp_bearings.delta_bearing())

    return delta_diff > rotate_threshold


def rotate_check(comp_bearings, rotate_threshold):
    """Check if the vessel is currently rotating."""
    return abs(comp_bearings.delta_bearing()) > rotate_threshold
