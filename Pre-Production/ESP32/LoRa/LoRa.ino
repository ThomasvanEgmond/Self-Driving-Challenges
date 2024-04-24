#include <SPI.h>
#include <LoRa.h>
#include "ds3231.h"
#include <SD.h>
#include <PS4Controller.h>
#include <ArduinoJson.h>
#include <Arduino.h>


OLED_CLASS_OBJ display(OLED_ADDRESS, OLED_SDA, OLED_SCL);

#define LORA_SENDER 1 // 0 receiving, 1 sending
#define LORA_PERIOD 433
#define LORA_V1_6_OLED  1

void onEvent();

const byte numChars = 64;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

      // variables to hold the parsed data
float timeMS = 0;
char stateChars[numChars] = {0};
int motorPWM = 0;
int brakePWM = 0;
float steeringDegrees = 0.0;
String state = "";
boolean newData = false;
JsonDocument controllerDataJson;
String controllerDataString;

void setup()
{
    Serial.begin(115200);
    if (LORA_SENDER){
      PS4.attach(onEvent);
      PS4.begin("f0:b6:1e:79:0b:4d");
    }
    while (!Serial);

    if (OLED_RST > 0) {
        pinMode(OLED_RST, OUTPUT);
        digitalWrite(OLED_RST, HIGH);
        delay(100);
        digitalWrite(OLED_RST, LOW);
        delay(100);
        digitalWrite(OLED_RST, HIGH);
    }

    display.init();
    display.flipScreenVertically();
    display.clear();
    display.setFont(ArialMT_Plain_16);
    display.setTextAlignment(TEXT_ALIGN_CENTER);
    display.drawString(display.getWidth() / 2, display.getHeight() / 2, LORA_SENDER ? "LoRa Sender" : "LoRa Receiver");
    display.display();
    delay(1000);

    String info = ds3231_test();
    if (info != "") {
        display.clear();
        display.setFont(ArialMT_Plain_16);
        display.setTextAlignment(TEXT_ALIGN_CENTER);
        display.drawString(display.getWidth() / 2, display.getHeight() / 2, info);
        display.display();
        delay(1000);
    }

    SPI.begin(CONFIG_CLK, CONFIG_MISO, CONFIG_MOSI, CONFIG_NSS);
    LoRa.setPins(CONFIG_NSS, CONFIG_RST, CONFIG_DIO0);
    if (!LoRa.begin(BAND)) {
        Serial.println("Starting LoRa failed!");
        while (1);
    }
    if (!LORA_SENDER) {
        display.clear();
        display.drawString(display.getWidth() / 2, display.getHeight() / 2, "LoraRecv Ready");
        display.display();
    }
}

void loop(){
  // delay(1);
  recvWithStartEndMarkers();
  if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
        showParsedData();
        newData = false;
    }
  #if LORA_SENDER
      // Gebruik deze zend code voor de knop en controller input, data = "tekst, 1, 1.00"
      // char data[64]
      controllerDataJson.shrinkToFit();
      serializeJson(controllerDataJson, controllerDataString);
      Serial.println(controllerDataString.length());
      LoRa.beginPacket();
      LoRa.print(controllerDataString);
      // LoRa.print("<" + "");
      LoRa.endPacket();
      
  #else
      if (LoRa.parsePacket()) {
          String recv = "";
          int i = 0;
          while (LoRa.available()) {
            char temp = (char)LoRa.read();
            recv += temp;
            receivedChars[i++] = temp;
          }
          receivedChars[i] = '\0';
          strcpy(tempChars, receivedChars);
          Serial.println(tempChars);
          // parseData();
          // showParsedData();
      }
  #endif
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void parseData() {      // split the data into its parts
    char * strtokIndx; // this is used by strtok() as an index

  // In order of sending,
    strtokIndx = strtok(tempChars,",");      // get the first part - the string
  // Int
    motorPWM = atoi(strtokIndx);     // convert this part to an integer
  // Int
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    brakePWM = atoi(strtokIndx);     // convert this part to an integer
  // Float
    strtokIndx = strtok(NULL, ",");
    steeringDegrees = atof(strtokIndx);     // convert this part to a float
  // String
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    strcpy(stateChars, strtokIndx); // copy it to messageFromPC
    state = stateChars;
    state.trim();

  #if LORA_SENDER
      LoRa.beginPacket();
      LoRa.print(receivedChars);
      LoRa.endPacket();
  #endif
}

void showParsedData() {
    display.clear();
    display.drawString(display.getWidth() / 2, display.getHeight() / 2 - 16, String(String(motorPWM) + " " +  String(brakePWM)));
    display.drawString(display.getWidth() / 2, display.getHeight() / 2, String(steeringDegrees, 5));
    // display.drawString(display.getWidth() / 2, display.getHeight() / 2, String(timeMS, 3));
    display.drawString(display.getWidth() / 2, display.getHeight() / 2 + 16, state);
    display.display();
}

void onEvent(){

  // controllerDataJson["Right"] = PS4.Right();
  // controllerDataJson["Down"] = PS4.Down();
  // controllerDataJson["Up"] = PS4.Up();
  // controllerDataJson["Left"] = PS4.Left();
  // controllerDataJson["Square"] = PS4.Square();
  // controllerDataJson["Cross"] = PS4.Cross();
  // controllerDataJson["Circle"] = PS4.Circle();
  // controllerDataJson["Triangle"] = PS4.Triangle();
  // controllerDataJson["L1"] = PS4.L1();
  // controllerDataJson["R1"] = PS4.R1();
  // controllerDataJson["L2"] = PS4.L2();
  // controllerDataJson["R2"] = PS4.R2();
  // controllerDataJson["Share"] = PS4.Share();
  // controllerDataJson["Options"] = PS4.Options();
  // controllerDataJson["L3"] = PS4.L3();
  // controllerDataJson["R3"] = PS4.R3();
  // controllerDataJson["PSButton"] = PS4.PSButton();
  // controllerDataJson["Touchpad"] = PS4.Touchpad();
  controllerDataJson["L2"] = PS4.L2Value();
  controllerDataJson["R2"] = PS4.R2Value();
  controllerDataJson["LX"] = PS4.LStickX();
  controllerDataJson["LY"] = PS4.LStickY();
  controllerDataJson["RX"] = PS4.RStickY();
  controllerDataJson["RY"] = PS4.RStickY();
  // Serial.println(float(controllerDataJson["R2Value"]));
  // Serial.println("AA");
  
  // if(PS4.LStickX()<-10||PS4.LStickX()>10||PS4.LStickY()<-10||PS4.LStickY()>10){
  //   printf("LStick: (%d, %d) \n", PS4.LStickX(), PS4.LStickY());
  // }

  // if(PS4.RStickX()<-10||PS4.RStickX()>10||PS4.RStickY()<-10||PS4.RStickY()>10){
  //   printf("RStick: (%d, %d) \n", PS4.RStickX(), PS4.RStickY());
  // }
}
