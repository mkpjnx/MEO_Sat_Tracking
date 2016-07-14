/*
 * Libraries and parts of code from:
 *  https://github.com/adafruit/Adafruit_Sensor
 *  https://github.com/adafruit/Adafruit_BNO055
 *  https://github.com/adafruit/Adafruit_MMA8451_Library
 */

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (1000)

Adafruit_BNO055 bno = Adafruit_BNO055(55);

void setup(void) 
{
  Serial.begin(9600);
  if(!bno.begin())
  {
    Serial.print("BNO055 not detected!");
    while(1);
  }
  delay(1000);
}

void loop() 
{
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
