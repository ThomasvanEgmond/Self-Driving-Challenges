int PUL = 7;  // welke kleur kabel?
int DIR = 6;  // welke kleur kabel?
int EN = 5;   // welke kleur kabel?

void setup() {
  Serial.begin(9600);
  pinMode (PUL, OUTPUT);
  pinMode (DIR, OUTPUT);
  pinMode (EN, OUTPUT);
  //digitalWrite(EN, HIGH);
}
void loop() {
  Serial.println("Voer stuurwaarde in: ");
  while (Serial.available() == 0) {}  // wachten tot er een waarde ingevoerd wordt
  int val = 0;
  if (Serial.available() > 0) {       // als er een waarde wordt ingevoerd, dan...
    val = Serial.parseInt();
    Serial.println(val);              // print stuurwaarde
    digitalWrite(DIR, LOW);
    for (int i = 0; i < val; i++)
    {
      digitalWrite(PUL, HIGH);
      delay(3);
      digitalWrite(PUL, LOW);
      delay(3);
      Serial.println("PUL low");
    }
    delay(1000);
    digitalWrite(DIR, HIGH);
    for (int i = 0; i < val; i++)
    {
      digitalWrite(PUL, HIGH);
      delay(3);
      digitalWrite(PUL, LOW);
      delay(3);
      Serial.println("PUL high");
    }
    delay(1000);

  }
}