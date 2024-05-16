const int ledPin = 9;  //pin 9 has PWM funtion

int value = 0;
void setup(){
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT); 
  // pinMode(potPin, INPUT); //Optional 
}

void loop(){
  while (Serial.available() == 0) {
  }
  value = Serial.parseInt();
  // if (value > 50){
  //   value = 5;
  // }
  // value = analogRead(potPin);          //Read and save analog value from potentiometer
  // value = map(value, 0, 1023, 0, 255); //Map value 0-1023 to 0-255 (PWM)
  analogWrite(ledPin, value);          //Send PWM value to led
  Serial.println(value);
}