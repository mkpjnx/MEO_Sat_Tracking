The attached file is a python library for accessing a GPS module through a serial port and parsing
the data for desirable information. 

In order for it to work properly, there are a few settings you need to manipulate in your GPS and your code
1. Set GPS unit to output GPRMC (Recommended Minimum) data only
2. Set the output frequency of your GPS to coincide with the sampling interval in your code in order to
properly read all lines sent by the GPS without buffer
3. Make sure to call the refresh() function of the GPS after every sampling iteration in your code
in order to properly access the most recent information sent by the GPS
4. You should only try to read data from the GPS if the fix state is True, but if for any reason the GPS sends
strange data the class will return None for any missing values

lenLatLon(lat)   -   Return length of one degree of latitude and longitude (in meters!!!) as a function of latitude
bearingLL(lat1, lon1, lat2, lon2) -   Return bearing of vector between two lat/lon points 
				      using linear approximation (In degrees E of N)
distanceLL(lat1, lon1, lat2, lon2)-   Return distance between two lat/lon points using linear 
				      approximation (In meters!!!)

GPS Class:
Initialization: GPS(port, baud)  -   initialize GPS with the serial port it is connected to and the 
 				     baudrate (you will probably want it to be 9600)
Function calls:
GPS.refresh()         -   Read most recent line sent by GPS into a list (call this after every sampling iteration)
GPS.isFixed()         -   Check fix state of GPS and return True if fixed and False if not
GPS.getLat()          -   Return latitude in degrees as a float
GPS.getLon()          -   Return longitude in degrees as a float
GPS.getTime()         -   Return current time (in UTC!!!) as a formatted string (HH:MM:SS.SSS)
GPS.getDate()         -   Return date of latest fix as a formatted string (DD/MM/YY)
GPS.getSpeed()        -   Return speed in knots as a float (calculated differentially by the GPS unit)
GPS.getBearing()      -   Return bearing in degrees as a float***
GPS.getMagVariation() -   Return magnetic variation at location - add the value returned from this function 
		          to your magnetic bearing to get true bearing (not exactly sure how accurate)


***GPS actually returns 'Course made good', which is really the direction of its movement, and does not necessarily 
translate to bearing