void setup() {
  Serial.begin(115200);
}

void loop() {
  Serial.println("$GPRMC,081836,A,3751.65,S,14507.36,E,000.0,360.0,130998,011.3,E*62,131.76");
  delay(500);
}
