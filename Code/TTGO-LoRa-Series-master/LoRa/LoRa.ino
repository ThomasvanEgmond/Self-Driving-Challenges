#include <SPI.h>
#include <LoRa.h>
#include "ds3231.h"
#include <SD.h>

OLED_CLASS_OBJ display(OLED_ADDRESS, OLED_SDA, OLED_SCL);

#define LORA_SENDER 0
#define LORA_PERIOD 433
#define LORA_V1_6_OLED  1

void setup()
{
    Serial.begin(115200);
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
    delay(2000);

    if (SDCARD_CS >  0) {
        display.clear();
        SPIClass sdSPI(VSPI);
        sdSPI.begin(SDCARD_SCLK, SDCARD_MISO, SDCARD_MOSI, SDCARD_CS);
        if (!SD.begin(SDCARD_CS, sdSPI)) {
            display.drawString(display.getWidth() / 2, display.getHeight() / 2, "SDCard  FAIL");
        } else {
            display.drawString(display.getWidth() / 2, display.getHeight() / 2 - 16, "SDCard  PASS");
            uint32_t cardSize = SD.cardSize() / (1024 * 1024);
            display.drawString(display.getWidth() / 2, display.getHeight() / 2, "Size: " + String(cardSize) + "MB");
        }
        display.display();
        delay(2000);
    }


    String info = ds3231_test();
    if (info != "") {
        display.clear();
        display.setFont(ArialMT_Plain_16);
        display.setTextAlignment(TEXT_ALIGN_CENTER);
        display.drawString(display.getWidth() / 2, display.getHeight() / 2, info);
        display.display();
        delay(2000);
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

int count = 0;

void loop()
{
#if LORA_SENDER
    int ms = millis();
    display.clear();
    display.setTextAlignment(TEXT_ALIGN_CENTER);
    display.drawString(display.getWidth() / 2, display.getHeight() / 2, String(ms));
    display.drawString(display.getWidth() / 2, display.getHeight() / 2 - 16, "millis():");
    display.display();
    LoRa.beginPacket();
    LoRa.print(ms);
    LoRa.endPacket();
#else
    if (LoRa.parsePacket()) {
        String recv = "";
        while (LoRa.available()) {
            recv += (char)LoRa.read();
        }
        count++;
        display.clear();
        display.drawString(display.getWidth() / 2, display.getHeight() / 2 + 16, recv);
        display.drawString(display.getWidth() / 2, display.getHeight() / 2, "Received:");
        String info = "[" + String(count) + "]" + "RSSI " + String(LoRa.packetRssi());
        display.drawString(display.getWidth() / 2, display.getHeight() / 2 - 16, info);
        display.display();
    }
#endif
}
