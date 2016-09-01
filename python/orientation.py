"""Takes in 9DOF data and parses input
"""

import math
import ephem

class orientation:


    def __init__(self, sentence):
        '''Initialize with the unparsed sentence'''
        self.unparsed = sentence
        self.info = sentence.split(',')

    def get_heading(self):
        """Return heading (E of N) in degrees as a float."""
        try:
            return float(self.info[1])

        except:
            return None

    def get_roll(self):
        """Return roll (counterclockwise) in degrees as a float."""
        try:
            return float(self.info[2])

        except:
            return None

    def get_pitch(self):
        """Return pitch (positive downwards) in degrees as a float."""
        try:
            return float(self.info[3])

        except:
            return None

    def get_calibration(self):
        try:
            return self.info[4:]
        except:
            return None
