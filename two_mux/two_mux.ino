// -------- SHARED SELECT LINES --------
const int SEL_A = 2;   // Connected to A of BOTH CD4051
const int SEL_B = 3;   // Connected to B of BOTH CD4051
const int SEL_C = 4;   // Connected to C of BOTH CD4051

// -------- MUX OUTPUTS --------
const int MUX1_OUT = A0;  // Z pin of U2
const int MUX2_OUT = A1;  // Z pin of U3

// -------- TOTAL SENSORS --------
const int NUM_SENSORS = 12;
int sensorValues[NUM_SENSORS];

// -------- CHANNEL SELECT --------
void selectChannel(uint8_t ch) {
  digitalWrite(SEL_A, ch & 0x01);
  digitalWrite(SEL_B, ch & 0x02);
  digitalWrite(SEL_C, ch & 0x04);
}

void setup() {
  pinMode(SEL_A, OUTPUT);
  pinMode(SEL_B, OUTPUT);
  pinMode(SEL_C, OUTPUT);

  digitalWrite(SEL_A, LOW);
  digitalWrite(SEL_B, LOW);
  digitalWrite(SEL_C, LOW);

  Serial.begin(9600);
  Serial.println("Dual CD4051 Shared ABC Proteus Simulation");
}

void loop() {

  int idx = 0;

  // -------- CHANNELS 0–7 --------
  for (int ch = 0; ch < 8; ch++) {
    selectChannel(ch);
    delayMicroseconds(10);

    // Read MUX1 (U2)
    int sum1 = 0;
    for (int i = 0; i < 5; i++) {
      sum1 += analogRead(MUX1_OUT);
      delayMicroseconds(100);
    }
    sensorValues[idx++] = sum1 / 5;

    // Read MUX2 (U3) – only first 4 channels used
    
    if (ch < 4) {
      int sum2 = 0;
      for (int i = 0; i < 5; i++) {
        sum2 += analogRead(MUX2_OUT);
        delayMicroseconds(100);
      }
      sensorValues[idx++] = sum2 / 5;
    }
  }

  // -------- SEND CSV --------
  for (int i = 0; i < NUM_SENSORS; i++) {
    Serial.print(sensorValues[i]);
    if (i < NUM_SENSORS - 1) Serial.print(",");
  }
  Serial.println();

  delay(300);
}
