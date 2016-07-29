import math
import gps

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
          	__ = self.b.pop()
        
    # This stuff is for drift (maybe, we'll see how it goes)
    def delta_bearing(self):
        """Find the change in bearing."""
        return(self.b[0]-self.b[1])

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
        """Return most recent calculated bearing based on GPS coordinates"""
        """In degrees East of North"""

        #Find length of one degree of latitude and longitude based on average of two most recent latitudes
        latlen, lonlen = gps.len_lat_lon((self.lats[0] + self.lats[1]) / 2)
        x = (self.longs[0] - self.longs[1]) * lonlen
        y = (self.lats[0] - self.lats[1]) * latlen
        
        b = 90 - math.degrees(math.atan2(y, x)) #Bearing in degrees East of North        

        return b % 360

    def lock(self):
        self.lats[0] = self.lats[1]
        self.longs[0] = self.longs[1]

    def get_dist_travelled(self):
        """Return distance between two most recent points"""

        latlen, lonlen = gps.len_lat_lon((self.lats[0] + self.lats[1]) / 2)
        x = (self.longs[0] - self.longs[1]) * lonlen
        y = (self.lats[0] - self.lats[1]) * latlen

        d = ((x * x) + (y * y)) ** .5
        return(d)
      
##def rotation_check(gpsBearing, compBearing):
##    deltaGPS = gpsBearing.delta_bearing()
##    deltaComp = compBearing.delta_bearing()
##    allowedVariation = 10 # will be adjusted based on experiment
##
##    if(abs(deltaComp) > 5): # <-- change 0 to rotation threshold
##        if(abs(deltaGPS - deltaComp) > allowedVariation):
##            print("Stationary rotation is occuring (maybe)")
##            return True
##        else:
##            print("Turning is occuring (maybe)")
##
##    else:
##        print("No rotation is occuring (probably)")
##        return False
##
##def drift_check(gpsBearing, compBearing):
##    deltaGPS = gpsBearing.delta_bearing()
##    deltaComp = compBearing.delta_bearing()
##    allowedVariation = 10 # this number will be changed based on experiments
##    if(abs(deltaGPS) > 5): # <-- rotation threshold
##        if(abs(deltaGPS - deltaComp) > allowedVariation):
##            print("Drift is occuring (maybe)")
##            return True
##        else:
##            print("No drift is occuring (probably)")
##            return False
##    else:
##        print("No drift is occuring (probably)")
##        return False
