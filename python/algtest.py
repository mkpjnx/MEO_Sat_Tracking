import time
import ephem
#import serial
import io
import sys
import string
import geomag

deg = ephem.degrees()
def get_raw_hdg():
    return 0.0 #Ephem degrees

def get_lat_lon():
    return 0.0, 0.0 #Ephem degrees

def get_tru_heading(raw, lat, lon):
    return raw - geomag.declination(lat,lon)*ephem.degree
