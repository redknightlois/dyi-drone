/*
 * Right Motors Test Demo - SimulIDE Compatible
 *
 * Simulates front-right and back-right drone motors using PWM.
 * Connect DC motors or LEDs to pins 9 and 10 in SimulIDE.
 *
 * Circuit in SimulIDE:
 *   - Pin 9  -> DC Motor (Front-Right) or LED with resistor
 *   - Pin 10 -> DC Motor (Back-Right) or LED with resistor
 *
 * Cycles through tests automatically every 5 seconds.
 */

const int FRONT_RIGHT_PIN = 9;
const int BACK_RIGHT_PIN = 10;

const unsigned long TEST_INTERVAL = 5000;

int currentTest = 0;

void setup() {
  pinMode(FRONT_RIGHT_PIN, OUTPUT);
  pinMode(BACK_RIGHT_PIN, OUTPUT);

  // Start with motors off
  analogWrite(FRONT_RIGHT_PIN, 0);
  analogWrite(BACK_RIGHT_PIN, 0);
}

void loop() {
  runTest(currentTest);
  delay(TEST_INTERVAL);

  currentTest++;
  if (currentTest > 5) {
    currentTest = 0;
  }
}

void runTest(int test) {
  switch (test) {
    case 0:
      // All off
      analogWrite(FRONT_RIGHT_PIN, 0);
      analogWrite(BACK_RIGHT_PIN, 0);
      break;

    case 1:
      // Front-right low speed
      analogWrite(FRONT_RIGHT_PIN, 100);
      analogWrite(BACK_RIGHT_PIN, 0);
      break;

    case 2:
      // Back-right low speed
      analogWrite(FRONT_RIGHT_PIN, 0);
      analogWrite(BACK_RIGHT_PIN, 100);
      break;

    case 3:
      // Both low speed
      analogWrite(FRONT_RIGHT_PIN, 100);
      analogWrite(BACK_RIGHT_PIN, 100);
      break;

    case 4:
      // Both medium speed
      analogWrite(FRONT_RIGHT_PIN, 180);
      analogWrite(BACK_RIGHT_PIN, 180);
      break;

    case 5:
      // Both high speed
      analogWrite(FRONT_RIGHT_PIN, 255);
      analogWrite(BACK_RIGHT_PIN, 255);
      break;
  }
}
