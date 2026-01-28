/*
 * 4 Motors Test Demo - SimulIDE Compatible
 *
 * Tests all 4 drone motors using PWM via two L298P drivers.
 *
 * Circuit in SimulIDE:
 *   - Pin 9  -> Motor Front-Right (EnA of right L298P)
 *   - Pin 10 -> Motor Back-Right (EnB of right L298P)
 *   - Pin 5  -> Motor Front-Left (EnA of left L298P)
 *   - Pin 6  -> Motor Back-Left (EnB of left L298P)
 *
 * Cycles through tests automatically every 2.5 seconds.
 */

const int FRONT_RIGHT_PIN = 9;
const int BACK_RIGHT_PIN = 10;
const int FRONT_LEFT_PIN = 5;
const int BACK_LEFT_PIN = 6;

const unsigned long TEST_INTERVAL = 2500;

const int SPEED_LOW = 100;
const int SPEED_MEDIUM = 180;
const int SPEED_HIGH = 255;

int currentTest = 0;
const int TOTAL_TESTS = 12;

void setup() {
  pinMode(FRONT_RIGHT_PIN, OUTPUT);
  pinMode(BACK_RIGHT_PIN, OUTPUT);
  pinMode(FRONT_LEFT_PIN, OUTPUT);
  pinMode(BACK_LEFT_PIN, OUTPUT);

  setAllMotors(0);
}

void loop() {
  runTest(currentTest);
  delay(TEST_INTERVAL);

  currentTest++;
  if (currentTest >= TOTAL_TESTS) {
    currentTest = 0;
  }
}

void setAllMotors(int speed) {
  analogWrite(FRONT_RIGHT_PIN, speed);
  analogWrite(BACK_RIGHT_PIN, speed);
  analogWrite(FRONT_LEFT_PIN, speed);
  analogWrite(BACK_LEFT_PIN, speed);
}

void runTest(int test) {
  switch (test) {
    case 0:
      // All off
      setAllMotors(0);
      break;

    case 1:
      // Front-right only
      setAllMotors(0);
      analogWrite(FRONT_RIGHT_PIN, SPEED_MEDIUM);
      break;

    case 2:
      // Back-right only
      setAllMotors(0);
      analogWrite(BACK_RIGHT_PIN, SPEED_MEDIUM);
      break;

    case 3:
      // Front-left only
      setAllMotors(0);
      analogWrite(FRONT_LEFT_PIN, SPEED_MEDIUM);
      break;

    case 4:
      // Back-left only
      setAllMotors(0);
      analogWrite(BACK_LEFT_PIN, SPEED_MEDIUM);
      break;

    case 5:
      // Right side (both right motors)
      setAllMotors(0);
      analogWrite(FRONT_RIGHT_PIN, SPEED_MEDIUM);
      analogWrite(BACK_RIGHT_PIN, SPEED_MEDIUM);
      break;

    case 6:
      // Left side (both left motors)
      setAllMotors(0);
      analogWrite(FRONT_LEFT_PIN, SPEED_MEDIUM);
      analogWrite(BACK_LEFT_PIN, SPEED_MEDIUM);
      break;

    case 7:
      // Front motors (both front motors)
      setAllMotors(0);
      analogWrite(FRONT_RIGHT_PIN, SPEED_MEDIUM);
      analogWrite(FRONT_LEFT_PIN, SPEED_MEDIUM);
      break;

    case 8:
      // Back motors (both back motors)
      setAllMotors(0);
      analogWrite(BACK_RIGHT_PIN, SPEED_MEDIUM);
      analogWrite(BACK_LEFT_PIN, SPEED_MEDIUM);
      break;

    case 9:
      // All motors low speed
      setAllMotors(SPEED_LOW);
      break;

    case 10:
      // All motors medium speed
      setAllMotors(SPEED_MEDIUM);
      break;

    case 11:
      // All motors high speed
      setAllMotors(SPEED_HIGH);
      break;
  }
}
