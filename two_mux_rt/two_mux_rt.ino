// -------- SHARED SELECT LINES --------
const int SEL_A = 2;
const int SEL_B = 3;
const int SEL_C = 4;

// -------- MUX OUTPUTS --------
const int MUX1_OUT = A0;
const int MUX2_OUT = A1;
const int MUX3_OUT = A2;
const int MUX4_OUT = A3;

// -------- TOTAL SENSORS --------
const int NUM_SENSORS = 32;
int sensorValues[NUM_SENSORS];

// -------- CHANNEL SELECT --------
void selectChannel(uint8_t ch) {
  digitalWrite(SEL_A, ch & 0x01);
  digitalWrite(SEL_B, (ch >> 1) & 0x01);
  digitalWrite(SEL_C, (ch >> 2) & 0x01);
}

void setup() {

  pinMode(SEL_A, OUTPUT);
  pinMode(SEL_B, OUTPUT);
  pinMode(SEL_C, OUTPUT);

  digitalWrite(SEL_A, LOW);
  digitalWrite(SEL_B, LOW);
  digitalWrite(SEL_C, LOW);

  Serial.begin(9600);
  Serial.println("4x CD4051 - 32 Sensor Reading");
}

void loop() {

  int idx = 0;

  // -------- CHANNELS 0–7 --------
  for (int ch = 0; ch < 8; ch++) {

    selectChannel(ch);
    delayMicroseconds(10);

    // ---- MUX1 ----
    int sum1 = 0;
    for (int i = 0; i < 5; i++) {
      sum1 += analogRead(MUX1_OUT);
      delayMicroseconds(100);
    }
    sensorValues[idx++] = sum1 / 5;

    // ---- MUX2 ----
    int sum2 = 0;
    for (int i = 0; i < 5; i++) {
      sum2 += analogRead(MUX2_OUT);
      delayMicroseconds(100);
    }
    sensorValues[idx++] = sum2 / 5;

    // ---- MUX3 ----
    int sum3 = 0;
    for (int i = 0; i < 5; i++) {
      sum3 += analogRead(MUX3_OUT);
      delayMicroseconds(100);
    }
    sensorValues[idx++] = sum3 / 5;

    // ---- MUX4 ----
    int sum4 = 0;
    for (int i = 0; i < 5; i++) {
      sum4 += analogRead(MUX4_OUT);
      delayMicroseconds(100);
    }
    sensorValues[idx++] = sum4 / 5;
  }

  // -------- SEND CSV --------
  for (int i = 0; i < NUM_SENSORS; i++) {
    Serial.print(sensorValues[i]);
    if (i < NUM_SENSORS - 1) Serial.print(",");
  }
  Serial.println();

  delay(300);
}