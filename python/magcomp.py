from geomag import geomag

dlat = 41.787
dlon = -88.355
h = 0

gm = geomag.GeoMag()
magobj = gm.GeoMag(dlat,dlon,h=h)
magvector = [magobj.bx/1000, magobj.by/1000, magobj.bz/1000]
print(magvector)
