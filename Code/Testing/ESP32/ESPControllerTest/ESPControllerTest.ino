#include <PS4Controller.h>
// #include <Arduino.h>

// int waardePotmeter = 0;                             // Waarde potmeter
int motorPin = 32;
int retractBrakeActuatorPin = 25;
int extendBrakeActuatorPin = 26;
int lowerMotorPWM = 65;
int upperMotorPWM = 115;
int retractionTimeMillis = 2400;
int lastKnownBrakeTime = 0;
int stepperPin = 2;
int motorPWM = 0;
bool doneBraking = true;

void setup() {
  Serial.begin(115200);
  PS4.attach(onEvent);                                // Koppel functie aan PS4 controller zodat deze actie wordt uitgevoerd als er een input is
  PS4.begin("f0:b6:1e:79:0b:4d");                     // ESP32 bootst MAC-address na
  // put your setup code here, to run once:
  pinMode(motorPin, OUTPUT);                                 // Motor output
  pinMode(extendBrakeActuatorPin, OUTPUT);                                 // Motor output
  pinMode(retractBrakeActuatorPin, OUTPUT);                                 // Motor output
  pinMode(stepperPin, OUTPUT);                                  // Servo input
  Serial.println("setup done");
}

void loop(){
  // Serial.println("loop");
  if (!PS4.L2Value() && motorPWM > 0) motorPWM--;
  delay(50);
}

void onEvent(){
  bool L1 = PS4.L1();
  if (L1){
    Serial.println("extending braking");
    analogWrite(retractBrakeActuatorPin, 0);
    analogWrite(extendBrakeActuatorPin, 120);                  // Waarde L2 toets wordt uitgelezen  
    lastKnownBrakeTime = millis();
  }

  if(!L1 && (millis() - lastKnownBrakeTime) <= retractionTimeMillis){
    doneBraking = false;
    Serial.println("retracting brake");
    analogWrite(extendBrakeActuatorPin, 0);  
    analogWrite(retractBrakeActuatorPin, 120);
  }
  else if(!L1 && !doneBraking){
    doneBraking = true;
    Serial.println("not braking");
    analogWrite(retractBrakeActuatorPin, 0);
  }

  if(PS4.L2Value()){
    Serial.print("L2: ");
    int l2PWM = PS4.L2Value();
    Serial.print(l2PWM);
    motorPWM = map(l2PWM, 0, 255, lowerMotorPWM, upperMotorPWM);
    Serial.print(" | motorPWM: ");
    Serial.println(motorPWM);
  }
  analogWrite(motorPin, motorPWM);                  // Waarde R2 toets wordt uitgelezen
}
// VOOR GEBRUIK POTMETER IS ONDERSTAAND SCRIPT VAN TOEPASSING
// waardePotmeter = analogRead(2);                  // Waarde potmeter uitlezen (in 1024)
// V = map(waardePotmeter, 0,1024,0,255);           // Herschalen van groot bereik (0-1024) naar klein bereik (0-255)
// analogWrite(1, V);