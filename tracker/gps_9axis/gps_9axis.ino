/* 
 * Libraries and parts of code from:
 *  https://github.com/adafruit/Adafruit_Sensor
 *  https://github.com/adafruit/Adafruit_BNO055
 *  https://github.com/adafruit/Adafruit_MMA8451_Library
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>
#include <utility/imumaths.h>

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (1000)

SoftwareSerial mySerial(8, 7);

Adafruit_BNO055 bno = Adafruit_BNO055(55);
Adafruit_GPS GPS(&mySerial);

#define GPSECHO false
boolean usingInterrupt = false;
void useInterrupt(boolean);

void setup(void) 
{
  Serial.begin(9600);
  if(!bno.begin())
  {
    Serial.print("BNO55 not detected!");
    while(1);
  }
  
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PGCMD_ANTENNA);
  useInterrupt(true);
  
  delay(1000);
}

SIGNAL(TIMER0_COMPA_vect) {
  char c = GPS.read();
  // if you want to debug, this is a good time to do it!
#ifdef UDR0
  if (GPSECHO)
    if (c) UDR0 = c;  
    // writing direct to UDR0 is much much faster than Serial.print 
    // but only one character can be written at a time. 
#endif
}

void useInterrupt(boolean v) {
  if (v) {
    // Timer0 is already used for millis() - we'll just interrupt somewhere
    // in the middle and call the "Compare A" function above
    OCR0A = 0xAF;
    TIMSK0 |= _BV(OCIE0A);
    usingInterrupt = true;
  } else {
    // do not call the interrupt function COMPA anymore
    TIMSK0 &= ~_BV(OCIE0A);
    usingInterrupt = false;
  }
}

uint32_t timer = millis();

void loop() 
{
  if (GPS.newNMEAreceived())
  {
    if (!GPS.parse(GPS.lastNMEA()))
      return;
  }

  if (timer > millis())  timer = millis();

  if (GPS.fix)
  {
    Serial.print(GPS.latitudeDegrees, 4); Serial.print(",");
    Serial.print(GPS.longitudeDegrees, 4); Serial.print(",");
  }
  else
  {
    Serial.print("0"); Serial.print(",");
    Serial.print("0"); Serial.print(",");
  }
  /* Get a new sensor event */ 
  sensors_event_t event; 
  bno.getEvent(&event);
  /* Write the heading/pitch/roll data to serial. */
  Serial.print((float)event.orientation.x); Serial.print(",");
  Serial.print((float)event.orientation.y); Serial.print(",");
  Serial.print((float)event.orientation.z); Serial.print(",");
  
  /* Write calibration data to serial. */
  uint8_t sys, gyro, accel, mag = 0;
  bno.getCalibration(&sys, &gyro, &accel, &mag);
  Serial.print(sys, DEC); Serial.print(",");
  Serial.print(gyro, DEC); Serial.print(",");
  Serial.print(accel, DEC); Serial.print(",");
  Serial.println(mag, DEC);
  
  delay(BNO055_SAMPLERATE_DELAY_MS);
  
}
