"""This module provides misc. functions for computing geodetic quantities."""
import math

def len_lat_lon(lat):
    """Return length of one degree of latitude and longitude.

    The lengths are a function of latitude.
    """
    # Constants for Fourier series approximation
    af1 = 111132.92
    af2 = -559.82
    af3 = 1.175
    af4 = -0.0023
    bf1 = 111412.84
    bf2 = -93.5
    bf3 = 0.118

    lat = math.radians(lat)

    # Fourier seriers that approximates lengths of one degree of lat and long
    lat_len = (af1 + (af2 * math.cos(2 * lat)) +
               (af3 * math.cos(4 * lat)) + (af4 * math.cos(6 * lat)))
    lon_len = ((bf1 * math.cos(lat)) + (bf2 * math.cos(3 * lat)) +
               (bf3 * math.cos(5 * lat)))
    return lat_len, lon_len


def bearing_lat_long(lat1, lon1, lat2, lon2):
    """Return bearing of vector between two lat/lon points. (In degrees E of N).

    Uses linear approximation.
    """
    # Use average of two latitudes to approximate distance
    # (Not very significant at smaller distances)
    lat_len, lon_len = len_lat_lon((lat1 + lat2) / 2)

    x_coord = (lon2 - lon1) * lon_len
    y_coord = (lat2 - lat1) * lat_len

    bearing = 90 - math.degrees(math.atan2(y_coord, x_coord))  # Bearing in degrees East of North
    return bearing


def distance_lat_lon(lat1, lon1, lat2, lon2):
    """Return distance between two lat/lon points using linear approximation.

    Distance is in meters.
    """
    lat_len, lon_len = len_lat_lon((lat1 + lat2) / 2)

    x_coord = (lon2 - lon1) * lon_len
    y_coord = (lat2 - lat1) * lat_len

    return ((x_coord * x_coord) + (y_coord * y_coord)) ** .5
  # Distance between points in meters
