int stripFeeder = 2;
int sprayer = 7;

void setup() {
  Serial.begin(9600);
  pinMode(stripFeeder, OUTPUT);
  pinMode(sprayer, OUTPUT);
}

void loop() {
  if (Serial.available() > 0 ){
    String msg = Serial.readString();

    // strip feeder solenoid valve
    if (msg == "1"){
      digitalWrite(stripFeeder, HIGH);
      delay(1000);
      digitalWrite(stripFeeder, LOW);
      delay(1000);
  
    }
    // sprayer 1 solenoid valve
    else if (msg == "3"){
      digitalWrite(sprayer, HIGH);
      // digitalWrite(LED_BUILTIN, HIGH);
      delay(1000);
      digitalWrite(sprayer, LOW);
      delay(1000);
    }
  }
}