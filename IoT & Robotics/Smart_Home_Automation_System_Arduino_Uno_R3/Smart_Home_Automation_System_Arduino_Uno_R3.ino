//Sensor

int IR = 2;
int pir = 7;
int fire_sensor = 11;

//equipments

int motor = 3;
int buzz2 = 8;      //Emergency Led / Red Led
int buzz1 = 4;    //Success Led / Green Led
int buzz3 = 12;

//Others

int trigPin = 9;
int echoPin = 10;
int duration, distance;

void setup() {
  pinMode(IR, INPUT);
  pinMode(pir, INPUT);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  Serial.begin(9600);
  
  pinMode(motor, OUTPUT);
  pinMode(buzz1, OUTPUT);
  pinMode(buzz2, OUTPUT);
  pinMode(buzz3, OUTPUT);
}

void loop() {
  //for IR sensor
  Serial.print("IR Sensor: ");
  Serial.println(digitalRead(IR));

  if(digitalRead(IR) == HIGH)
  {
    digitalWrite(buzz1, HIGH);
  }
  else
  {
    digitalWrite(buzz1, LOW);
  }

  //for ultrasonic sensor

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration*0.034/2;

  Serial.print("Distance in cm");
  Serial.println(distance);

  if(distance <= 5)
  {
    digitalWrite(motor, LOW);
  }
  if(distance >= 30)
  {
    digitalWrite(motor, HIGH);
  }
  else
  {
    digitalWrite(motor, LOW);
}

  //for pir sensor
  
  if(digitalRead(pir) == HIGH)
  {
    tone(buzz2, 30, 60);
  }
  if(digitalRead(pir) == LOW)
  {
    noTone(buzz2);
  }
  
  //for fire sensor

  if(digitalRead(fire_sensor) == LOW)
  {
    digitalWrite(buzz3, HIGH);
  }
  if(digitalRead(fire_sensor) == HIGH)
  {
    noTone(buzz3);
  }
}