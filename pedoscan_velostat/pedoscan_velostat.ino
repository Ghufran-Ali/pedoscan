// MUX select pins
const int S0 = 2;
const int S1 = 3;
const int S2 = 4;
const int S3 = 5;

// MUX common pin
const int muxAnalogPin = A0;

// Number of pressure sensors
const int NUM_SENSORS = 12;

// Store readings
int sensorValues[NUM_SENSORS];

// ------------------ MUX CHANNEL SELECT ------------------
void selectChannel(int channel) {
  digitalWrite(S0, channel & 0x01);
  digitalWrite(S1, channel & 0x02);
  digitalWrite(S2, channel & 0x04);
  digitalWrite(S3, channel & 0x08);
}

// ------------------ SETUP ------------------
void setup() {
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);

  Serial.begin(9600);
  Serial.println("Pedoscan Velostat Simulation Started");
}

// ------------------ LOOP ------------------
void loop() {

  for (int i = 0; i < NUM_SENSORS; i++) {
    selectChannel(i);
    delayMicroseconds(5);

    // Average readings for stability
    int sum = 0;
    for (int j = 0; j < 8; j++) {
      sum += analogRead(muxAnalogPin);
      delayMicroseconds(200);
    }

    sensorValues[i] = sum / 8;
  }

  // Send data as CSV
  for (int i = 0; i < NUM_SENSORS; i++) {
    Serial.print(sensorValues[i]);
    if (i < NUM_SENSORS - 1)
      Serial.print(",");
  }
  Serial.println();

  delay(300);
}
