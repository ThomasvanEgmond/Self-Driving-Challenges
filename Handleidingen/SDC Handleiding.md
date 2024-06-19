# SDC Handleiding

Dit is een korte handleiding over hoe je ons project werkend kan krijgen.

## Installeren

Als eerste download je de laatste versie van de code van [`de GitHub`](https://github.com/ThomasvanEgmond/Self-Driving-Challenges/tree/main/Code/Production)! Installeer Python 3.10 en alle benodigde packages.

Schaf twee [`LilyGO TTGO T3 LoRa32 433MHz V1.6.1`](https://www.tinytronics.nl/nl/development-boards/microcontroller-boards/met-lora/lilygo-ttgo-t3-lora32-433mhz-v1.6.1-esp32) aan.

Verbind een PS4 controller met je laptop, vind het MAC-adres van je bluetooth adapter en noteer deze. In de ESP code `ESP32.ino` verander je `PS4.begin("f0:b6:1e:79:0b:4d")` naar het MAC-adres van jouw laptops's bluetooth adapter. Verander ook `#define LORA_SENDER 0` om in te stellen of de ESP een LoRa sender of receiver is. Schakel nu de bluetooth van je laptop uit en flash de ESP code. Verbind de controller aan de sender ESP.

Verbind de ESP32 en de vier camera's (USB hub, let op een slechte USB hub kan problemen veroorzaken) aan de computer.

De camera's die zijn aangesloten aan de computer kunnen in de code alleen worden gedefinieerd met een getal. Als jouw camera's niet overeenkomen met de functie die ze hebben, het objectherkennings model gebruikt bijvoorbeeld de linker zij-camera moeten deze getallen worden omgewisseld.

Dit kan je doen in `Yolov8.py` bij `results = self.ov_model(source="0", show=True, verbose=False, imgsz=800, stream=True)` en dan gaat het om `source`. 

En in `lines.py` bij `self.camera_list.append(Camera("voor",1,141439, 4,'t', 'g', 'y', 'h', 'b'))` waar het gaat om de tweede parameter in dit geval dus `1`. In dezelfde lijn kan je ook de keybinds aanpassen voor het kalibreren van de lijndetectie camera's.

<img src="Controls voor camera's kalibreren.png" width="512">

## Gebruiken

Start simpelweg het `main.py` bestand! Heb geduld dit kan zeker twee minuten duren.

De kans is aanwezig dat je lijndetectie camera's niet goed staan ingesteld, gebruik dan de kalibratie toetsen om dit handmatig of automatisch te doen. Voor het automatisch kalibreren is het van belang dat je een wit voorwerp zoals een A4'tje laat zien. Verplaats het voorwerp zodat er meer of minder ruimte op het scherm wordt opgenomen door het witte voorwerp en blijf op de kalibratie knop klikken tot de camera naar wens is afgesteld.

Het is aangeraden om je camera van tevoren voor te bereiden door instellingen zoals automatische witbalans uit te zetten.

Op de ESP32 verbonden aan de computer zul je nu de gas, rem en stuur waardes zien. Dezelfde ESP ontvangt op dat moment ook data van de sender ESP waar de controller aan verbonden zit maar doet hier momenteel niks mee.