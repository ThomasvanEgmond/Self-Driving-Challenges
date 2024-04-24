#include <SPI.h>
#include <LoRa.h>
#include "ds3231.h"
#include <SD.h>
#include <PS4Controller.h>


OLED_CLASS_OBJ display(OLED_ADDRESS, OLED_SDA, OLED_SCL);

#define LORA_SENDER 0 // 0 receiving, 1 sending
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

void setup()
{
    Serial.begin(115200);
    PS4.attach(onEvent);
    PS4.begin("f0:b6:1e:79:0b:4d");
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
      // LoRa.beginPacket();
      // LoRa.print(data);
      // LoRa.endPacket();
  #else
      // if (LoRa.parsePacket()) {
      //     String recv = "";
      //     int i = 0;
      //     while (LoRa.available()) {
      //       char temp = (char)LoRa.read();
      //       recv += temp;
      //       receivedChars[i++] = temp;
      //     }
      //     receivedChars[i] = '\0';
      //     strcpy(tempChars, receivedChars);
      //     parseData();
      //     showParsedData();
      // }
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
 
  if(PS4.event.button_up.right){
    Serial.println("right arrow up");
  }
 
  if(PS4.event.button_down.right){
    Serial.println("right arrow down");
  }
 
  if(PS4.event.button_up.left){
    Serial.println("left arrow up");
  }
 
  if(PS4.event.button_down.left){
    Serial.println("left arrow down");
  }
 
  if(PS4.event.button_up.down){
    Serial.println("down arrow up");
  }
 
  if(PS4.event.button_down.down){
    Serial.println("down arrow down");
  }
 
  if(PS4.event.button_up.up){
    Serial.println("up arrow up");
  }
 
  if(PS4.event.button_down.up){
    Serial.println("up arrow down");
  }
 
  if(PS4.event.button_up.r3){
    Serial.println("r3 stick up");
  }
 
  if(PS4.event.button_down.r3){
    Serial.println("r3 stick down");
  }
 
  if(PS4.event.button_up.l3){
    Serial.println("l3 stick up");
  }
 
  if(PS4.event.button_down.l3){
    Serial.println("l3 stick down");
  }
 
  if(PS4.R2Value()){
    printf("R2: %d \n", PS4.R2Value());
  }
 
  if(PS4.L2Value()){
    printf("L2: %d \n", PS4.L2Value());
  }
 
  if(PS4.event.button_up.l1){
    Serial.println("l1 button up");
  }
 
  if(PS4.event.button_down.l1){
    Serial.println("l1 button down");
  }
 
  if(PS4.event.button_up.r1){
    Serial.println("r1 button up");
  }
 
  if(PS4.event.button_down.r1){
    Serial.println("r1 button down");
  }
 
  if(PS4.event.button_up.touchpad){
    Serial.println("touchpad button up");
  }
 
  if(PS4.event.button_down.touchpad){
    Serial.println("touchpad button down");
  }
 
  if(PS4.event.button_up.options){
    Serial.println("options button up");
  }
 
  if(PS4.event.button_down.options){
    Serial.println("options button down");
  }
 
  if(PS4.event.button_up.share){
    Serial.println("share button up");
  }
 
  if(PS4.event.button_down.share){
    Serial.println("share button down");
  }
 
  if(PS4.event.button_up.ps){
    Serial.println("ps button up");
  }
 
  if(PS4.event.button_down.ps){
    Serial.println("ps button down");
  }
 
  if(PS4.event.button_up.triangle){
    Serial.println("triangle button up");
  }
 
  if(PS4.event.button_down.triangle){
    Serial.println("triangle button down");
  }
 
  if(PS4.event.button_up.circle){
    Serial.println("circle button up");
  }
 
  if(PS4.event.button_down.circle){
    Serial.println("circle button down");
  }
 
  if(PS4.event.button_up.square){
    Serial.println("square button up");
  }
 
  if(PS4.event.button_down.square){
    Serial.println("square button down");
  }
 
  if(PS4.event.button_up.cross){
    Serial.println("cross button up");
  }
 
  if(PS4.event.button_down.cross){
    Serial.println("cross button down");
  }

  if(PS4.LStickX()<-10||PS4.LStickX()>10||PS4.LStickY()<-10||PS4.LStickY()>10){
    printf("LStick: (%d, %d) \n", PS4.LStickX(), PS4.LStickY());
  }

  if(PS4.RStickX()<-10||PS4.RStickX()>10||PS4.RStickY()<-10||PS4.RStickY()>10){
    printf("RStick: (%d, %d) \n", PS4.RStickX(), PS4.RStickY());
  }
}