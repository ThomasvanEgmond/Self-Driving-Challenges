# Self Driving Challenge 2024 (SDC2024) | TINPRJ0478

<img src=https://github.com/ThomasvanEgmond/Self-Driving-Challenges/assets/122525080/db6c1465-9d8f-425b-9c80-bc690afa91f6 width="360">
<img src=https://github.com/ThomasvanEgmond/Self-Driving-Challenges/assets/122525080/565898b2-9b51-4e34-864f-a222ab80e946 width="312">

Wij zijn Kadirhan Akin (1060024), David Akerboom (1056357), Luuk de Vries Reilingh (1053870) en Thomas van Egmond (1038854) en ons project 7/8 voor het tweede jaar Technische Informatica was de [`Self Driving Challenge 2024`](https://www.selfdrivingchallenge.nl/)!


## Self Driving Challenge?

De Self Driving Challenge (SDC) is een wedstrijd open voor hogescholen en universiteiten, georganiseerd door de Rijksdienst voor het Wegverkeer (RDW).

Het doel van de wedstrijd is om een autonoom rijdend voertuig te maken dat door de RDW gemaakte obstakels en scenario's kan passeren terwijl deze zich aan de opgelegde regels houdt!

De SDC bevat twee categorieën, de `closed category' en de 'open category'. Bij de closed category krijgt het studententeam een rijdende kart tot beschikken gesteld, voorzien van camera's, snelheid en stuurhoek sensoren, LiDAR en een Intel NUC computer. Bij de open category krijgt het studententeam dit niet en moeten zij zichzelf van een voertuig voorzien dat aan de door de RDW opgestelde eisen voldoet.

Wij van Hogeschool Rotterdam deden mee aan de open category. In samenwerking met Automotive en Werktuigbouwkunde studenten gingen wij zelf een kart bouwen en deze autonoom rijdend maken!

## Challenges? (obstakels en scenario's)

Zoals in de bovenstaand afbeelding is te zien bestaat de challenge uit zes verschillende obstakels, deze zijn onder te verdelen in de volgende scenario's:
1. Het tijdig stoppen bij een stopstreep als er een rood verkeerslicht is en vertrekken van deze stopstreep bij groen licht.
2. Snelheidsborden inlezen en onder deze maximum snelheid rijden.
3. Het detecteren van een voetganger die bij een voetgangersoversteekplaats staat en deze laten oversteken.
4. Het detecteren van een stilstaand voertuig op de rijbaan en deze passeren.
5. Fileparkeren in een vak.

### Hoe gaan we de challenges aanpakken?

1. Door gebruik te maken van YoloV8 een machine learning algoritme (zie 'YoloV8 en easyOCR' in het mapje 'Modules') dat wij trainen om rode en groene verkeerslichten te herkennen en hier onderscheid tussen te maken. In combinatie met een camera aan de voorzijde van de kart om lijnen te herkennen (zie 'Lijndetectie' in het mapje 'Modules'). YoloV8 een rood verkeerslicht ziet zal de kart langzaam gaan rijden tot deze een stopstreep herkent met de camera aan de voorzijde. De kart zal dan stoppen voor de stopstreep en wachten op groen licht, zodra het licht groen wordt zal de kart weer gaan rijden.

2. YoloV8 wordt ook getraind om snelheidsborden te herkennen. Het gedeelte van het beeld dat wordt herkent als snelheidsbord wordt daarna gescand door easyOCR een 'optical character recognition' model (zie 'YoloV8 en easyOCR' in het mapje 'Modules') dat de tekst van het snelheidsbord afleest.

3. YoloV8 wordt ook getraind om personen te herkennen. Net als bij de stoplichten, als YoloV8 een persoon ziet zal de kart langzaam gaan rijden tot deze het zebrapad herkent met de camera aan de voorzijde, dan zal de kart stoppen voor het zebrapad. De kart onthoudt aan welke kant de persoon staat en wacht tot deze naar de overzijde is gelopen en zal daaropvolgend weer gaan rijden. Is er geen zebrapad dan zal de kart langzaam de persoon passeren, zodra deze uit beeld is zal de kart weer gaan versnellen. 

4. Helaas in verband met complexiteit van dit probleem is het ons niet gelukt om een werkend prototype te maken dat dit obstakel kan trotseren. Wel hadden wij gepland om de stilstaande auto te herkennen met LiDAR en met behulp van die informatie de kart om de auto heen te sturen.

5. Helaas in verband met complexiteit van dit probleem is het ons niet gelukt om een werkend prototype te maken dat dit obstakel kan trotseren.

### RDW vereiste

De RDW heeft voor de open category eisen gesteld aan zowel hardware als software.

1. Het voertuig moet tussen autonome en handmatig bestuurde modus gewisseld kunnen worden, er moet dus ook een handmatig bestuurde modus aanwezig zijn. Om an deze vereiste te voldoen hebben we gebruik gemaakt van een ESP32's die beschikken over LoRa (Long Range). Over ons zelf opgestelde LoRa netwerk kunnen we input leveren om de kart de besturen door middel van een controller. Via deze controller kunnen we ook een input geven aan de kart om tussen besturing modi te wisselen. (zie 'LoRa ESP32 en Intel NUC' in het mapje 'Modules')

2. Het voertuig moet worden verzien van een lokale en een remote noodstop. Op het voertuig is een noodstop ingebouwd die handmatig de toevoer van stroom onderbreekt. Via een knop verbonden aan LoRa ESP32 kan en over het LoRa netwerk een noodstop signaal worden verstuurd naar de LoRa ESP32 op het voortuig. Na het ontvangen van dit signaal zou de LoRa ESP32 op het voertuig ook de stroom toevoer kunnen onderbreken, in werkelijkheid kan dit nog niet omdat de lokale noodstop niet via een signaal om te zetten is.

3. Het voertuig zelf moet aan een lijst een technische eisen voldoen te vinden in 'Self Driving Challenge 2024 - Information document'. Deze eisen zijn afgeleid van [`'168/2023, vehicle category L7e-C'`](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex%3A32013R0168).
