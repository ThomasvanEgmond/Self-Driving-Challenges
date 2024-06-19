#include <SPI.h>
#include <LoRa.h>
#include "ds3231.h"
#include <SD.h>
#include <PS4Controller.h> // https://github.com/pablomarquez76/PS4_Controller_Host


OLED_CLASS_OBJ display(OLED_ADDRESS, OLED_SDA, OLED_SCL);

#define LORA_SENDER 0 // 0 receiving, 1 sending
#define LORA_PERIOD 433
#define LORA_V1_6_OLED  1

void onEvent();

const byte numChars = 64;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing
char receivedCharsPC[numChars];
char tempCharsPC[numChars];
boolean newData = false;

int steeringAngle;
int motorPWM;
int brakePWM;

int r2 = 0;
int l2 = 0;
int lStickX = 0;
int lStickY = 0;

void setup(){
    Serial.begin(115200);
    if (LORA_SENDER) {
      PS4.attach(onEvent);
      PS4.begin("f0:b6:1e:79:0b:4d"); // make this the mac-address of the bluetooth adapter that your ps4 controller was last connected to, like your laptop. This will pretend to be your laptop, so turn off your laptop bluetooth.
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
  recvWithStartEndMarkers(); //receive data from PC on serial

  if (newData == true) { //checks for data from the PC on serial.
        strcpy(tempCharsPC, receivedCharsPC);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData(true);
        showParsedData();
        newData = false;
    }

  #if LORA_SENDER
      // Gebruik deze zend code voor de knop en controller input, data = "tekst, 1, 1.00";
        String data = String("<" + String(r2) + "," + String(r2) + "," + String(lStickX) + "," + String(lStickY) + ">");
        LoRa.beginPacket();
        LoRa.print(data);
        LoRa.endPacket();
        display.clear();
        // display.drawString(display.getWidth() / 2, display.getHeight() / 2 - 16, String("L2: " + String(l2) + " R2:" + String(r2)));
        display.drawString(display.getWidth() / 2, display.getHeight() / 2, data);
        // display.drawString(display.getWidth() / 2, display.getHeight() / 2 + 16, String("y: " + String(lStickY)));
        display.display();
      // }
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
          Serial.println(receivedChars);
          strcpy(tempChars, receivedChars);
          parseData(false);
          showParsedData();
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
                receivedCharsPC[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedCharsPC[ndx] = '\0'; // terminate the string
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

void parseData(bool fromPC) {      // split the data into its parts
  char * strtokIndx; // this is used by strtok() as an index
  
    // remove strtok from first variable

  // In order of sending,
  if (fromPC){
    strtokIndx = strtok(tempCharsPC,",");      // get the first part - the string
    // Int
    motorPWM = atoi(strtokIndx);     // convert this part to an integer

    // Int
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    brakePWM = atoi(strtokIndx);     // convert this part to an integer

    // Int
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    steeringAngle = atoi(strtokIndx);     // convert this part to an integer
  }
  
  else{
    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    // Int
    r2 = atoi(strtokIndx);     // convert this part to an integer
    // Serial.print(r2);

    // Int
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    r2 = atoi(strtokIndx);     // convert this part to an integer

    // Int
    strtokIndx = strtok(NULL, ",");
    lStickX = atoi(strtokIndx);     // convert this part to a integer

    // Int
    strtokIndx = strtok(NULL, ",");
    lStickY = atoi(strtokIndx);     // convert this part to a integer
  }

  // // Int
  //   strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  //   integerFromPC = atoi(strtokIndx);     // convert this part to an integer

  // // Float
  //   strtokIndx = strtok(NULL, ",");
  //   floatFromPC = atof(strtokIndx);     // convert this part to a float
  
  // // String
  //   strcpy(messageFromPcChar, strtokIndx); // copy it to messageFromPC
  //   messageFromPC = messageFromPcChar;
  //   messageFromPC.trim();

}

void showParsedData() {
    display.clear();
    String richting = "Voor ";
    String gas = "Gas los ";
    String rem = "Rem los ";
    if (steeringAngle < 90) richting = "Links ";
    if (steeringAngle > 90) richting = "Rechts ";
    if (motorPWM > 90) gas = "Gassen ";
    if (brakePWM > 90) rem = "Remmen ";
    display.drawString(display.getWidth() / 2, display.getHeight() / 2 - 16, String(gas + String(motorPWM)));
    display.drawString(display.getWidth() / 2, display.getHeight() / 2, String(rem + String(brakePWM)));
    display.drawString(display.getWidth() / 2, display.getHeight() / 2 + 16, String(richting + String(steeringAngle)));
    display.display();
}

void onEvent(){
  r2 = 0;
  l2 = 0;
  lStickX = 0;
  lStickY = 0;
 
  if(PS4.R2Value()){
    r2 = PS4.R2Value();
    // printf("R2: %d \n", PS4.R2Value());
  }
 
  if(PS4.L2Value()){
    l2 = PS4.L2Value();
    // printf("L2: %d \n", PS4.L2Value());
  }

  if(PS4.LStickX()<-10||PS4.LStickX()>10||PS4.LStickY()<-10||PS4.LStickY()>10){
    lStickX = PS4.LStickX();
    lStickY = PS4.LStickY();
    // printf("LStick: (%d, %d) \n", PS4.LStickX(), PS4.LStickY());
  }

  if(PS4.RStickX()<-10||PS4.RStickX()>10||PS4.RStickY()<-10||PS4.RStickY()>10){
    // printf("RStick: (%d, %d) \n", PS4.RStickX(), PS4.RStickY());
  }
}