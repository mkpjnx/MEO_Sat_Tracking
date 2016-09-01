
// Test code for Adafruit GPS modules using MTK3329/MTK3339 driver
//
// This code just echos whatever is coming from the GPS unit to the
// serial monitor, handy for debugging!
//
// Tested and works great with the Adafruit Ultimate GPS module
// using MTK33x9 chipset
//    ------> http://www.adafruit.com/products/746
// Pick one up today at the Adafruit electronics shop 
// and help support open source hardware & software! -ada

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>
// Connect the GPS Power pin to 5V
// Connect the GPS Ground pin to ground
// If using software serial (sketch example default):
//   Connect the GPS TX (transmit) pin to Digital 3
//   Connect the GPS RX (receive) pin to Digital 2
// If using hardware serial (e.g. Arduino Mega):
//   Connect the GPS TX (transmit) pin to Arduino RX1, RX2 or RX3
//   Connect the GPS RX (receive) pin to matching TX1, TX2 or TX3
SoftwareSerial mySerial(8, 7);
Adafruit_GPS GPS(&mySerial);
Adafruit_BNO055 bno = Adafruit_BNO055(55);
// If using hardware serial (e.g. Arduino Mega), comment
// out the above six lines and enable this line instead:
//Adafruit_GPS GPS(&Serial1);


// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO  false

// this keeps track of whether we're using the interrupt
// off by default!
boolean usingInterrupt = false;

void setup()  
{
  Serial.begin(115200);
  // 9600 NMEA is the default baud rate for MTK - some use 4800
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PMTK_API_SET_FIX_CTL_1HZ);
  GPS.sendCommand(PGCMD_NOANTENNA);
  
  if(!bno.begin())
  {
    /* There was a problem detecting the HMC5883 ... check your connections */
    Serial.println("Ooops, no BNO055 detected ... Check your wiring!");
    while(1);
  }
  delay(500);
}

// Interrupt is called once a millisecond, looks for any new GPS data, and stores it
/*SIGNAL(TIMER0_COMPA_vect) {
  char c = GPS.read();
  // if you want to debug, this is a good time to do it!
  if (GPSECHO)
    if (c) UDR0 = c;  
    // writing direct to UDR0 is much much faster than Serial.print 
    // but only one character can be written at a time. 
}*/

char nmea[300];
int index = 0;
unsigned long time = millis();
void loop()                     // run over and over again
{

  char c = GPS.read();
  if ( c == '$'){
    Serial.print("$");Serial.println(nmea);
    Serial.print("$");Serial.println(nmea);
    index = 0;
    nmea[0] = '\0';
  }
  else if (c && c != '\n' && c != '\r'){
    nmea[index++] = c;
    nmea[index] = '\0';
    //Serial.print(c);
  }
  
  if(millis()-time > 50){
    time = millis();
    sensors_event_t event; 
    bno.getEvent(&event);  
    uint8_t sys, gyro, accel, mag = 0;
    bno.getCalibration(&sys, &gyro, &accel, &mag);
    Serial.print("$IMU,");
    Serial.print((float)event.orientation.x); Serial.print(",");
    Serial.print((float)event.orientation.y); Serial.print(",");
    Serial.print((float)event.orientation.z); Serial.print(",");
    
    Serial.print(sys, DEC); Serial.print(",");
    Serial.print(gyro, DEC); Serial.print(",");
    Serial.print(accel, DEC); Serial.print(",");
    Serial.println(mag, DEC);
  }
  delay(1);
}

