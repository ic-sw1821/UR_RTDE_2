int stripFeeder = 2;
int sprayer = 7;

void setup() {
  Serial.begin(112500);
  pinMode(stripFeeder, OUTPUT);
  pinMode(sprayer, OUTPUT);
  digitalWrite(stripFeeder, HIGH);
  digitalWrite(sprayer, HIGH);
}

void loop() {
  if (Serial.available() > 0 ){
    String msg = Serial.readString();

    // strip feeder solenoid valve
    if (msg == "1"){
      digitalWrite(stripFeeder, LOW);
      delay(100);
      digitalWrite(stripFeeder, HIGH);
      Serial.println("Strip feeder activated");  
    }
    // sprayer 1 solenoid valve
    else if (msg == "3"){
      digitalWrite(sprayer, LOW);
      Serial.println("Sprayer ON");
    }
    else if (msg == "4"){
      digitalWrite(sprayer, HIGH);
      Serial.println("Sprayer OFF");
    }
  }
}

