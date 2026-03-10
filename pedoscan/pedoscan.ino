int fsrPin = A0;
int adcValue = 0;
float voltage = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  adcValue = analogRead(fsrPin);
  voltage = adcValue * (5.0 / 1023.0);

  Serial.print("ADC: ");
  Serial.print(adcValue);
  Serial.print("  | Voltage: ");
  Serial.println(voltage);

  delay(200);
}
