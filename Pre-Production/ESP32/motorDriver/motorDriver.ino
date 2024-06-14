const int motorPin = 32;  //pin 9 has PWM funtion

int value = 0;
void setup(){
  Serial.begin(9600);
  pinMode(motorPin, OUTPUT); 
  pinMode(26, OUTPUT); 
  pinMode(25, OUTPUT); 
  analogWrite(25, 0);
  analogWrite(26, 0);
  // pinMode(potPin, INPUT); //Optional 
}

void loop(){
  // for (int i = 0; i <= 70; i++){
  //   analogWrite(motorPin, i);
  //   Serial.println(i);
  //   delay(120);
  // }
  // // delay(5000);
  // for (int i = 70; i > 0; i--){
  //   analogWrite(motorPin, i);
  //   Serial.println(i);
  //   delay(120);
  // }
  while (Serial.available() == 0) {
  }
  value = Serial.parseInt();
  // if (value > 100){
  //   value = 5;
  // }
  // value = analogRead(potPin);          //Read and save analog value from potentiometer
  // value = map(value, 0, 1023, 0, 255); //Map value 0-1023 to 0-255 (PWM)
  analogWrite(motorPin, value);          //Send PWM value to led
  Serial.println(value);
}