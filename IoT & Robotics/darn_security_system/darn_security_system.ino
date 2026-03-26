#include <Servo.h>

#define TRIG_PIN 8
#define ECHO_PIN 9
#define BUZZER_PIN 6
#define SERVO_PIN 10
#define BUTTON_PIN 7

Servo doorServo;
bool alarmActive = false;

const int DIST_THRESHOLD = 5; // cm
unsigned long lastSirenTime = 0;
int sirenFreq = 500;
bool rising = true;

void setup() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP); // button connected to GND
  doorServo.attach(SERVO_PIN);
  doorServo.write(0); // door open

  Serial.begin(9600);
  Serial.println("System armed.");
}

void loop() {
  int distance = getDistance();
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Activate alarm if object is within threshold
  if (distance > 0 && distance <= DIST_THRESHOLD && !alarmActive) {
    alarmActive = true;
    Serial.println("⚠️ Intruder detected!");
    doorServo.write(90); // close door
    lastSirenTime = millis();
  }

  // Siren logic
  if (alarmActive) {
    playSiren();

    // Check if button is pressed to stop the alarm
    if (digitalRead(BUTTON_PIN) == LOW) {
      alarmActive = false;
      noTone(BUZZER_PIN);
      doorServo.write(0); // reopen door
      Serial.println("✔ Alarm stopped manually.");
      delay(500); // debounce
    }
  }
  delay(100);
}

int getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30 ms timeout
  if (duration == 0) return -1; // out of range
  return duration * 0.034 / 2;
}

void playSiren() {
  if (millis() - lastSirenTime > 30) {
    lastSirenTime = millis();
    tone(BUZZER_PIN, sirenFreq);
    sirenFreq += rising ? 20 : -20;
    if (sirenFreq >= 2000) rising = false;
    else if (sirenFreq <= 500) rising = true;
  }
}
