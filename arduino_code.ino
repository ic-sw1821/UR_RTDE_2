int stripFeeder = 2;
int sprayer = 4;
int powder = 6;
int signalPin = 8;

void setup() {
  Serial.begin(9600);
  pinMode(stripFeeder, OUTPUT);
  pinMode(sprayer, OUTPUT);
  pinMode(signalPin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0 ){
    String msg = Serial.readString();

    // strip feeder solenoid valve
    if (msg == "1"){
      // digitalWrite(stripFeeder, HIGH)
      digitalWrite(LED_BUILTIN, HIGH);
      delay(1000);
      // digitalWrite(stripFeeder, LOW)
      digitalWrite(LED_BUILTIN, LOW);
      delay(1000); 
    }
    // sprayer 1 solenoid valve
    else if (msg == "3"){
      // digitalWrite(sprayer, HIGH);
      digitalWrite(LED_BUILTIN, HIGH);
      delay(2000);
    }
    else if (msg == "4"){
      // digitalWrite(sprayer, LOW);
      digitalWrite(LED_BUILTIN, LOW);
      delay(2000);
    }
    // sprayer 2 powder solenoid valve
    else if (msg == "5"){
      // digitalWrite(powder, HIGH)
      digitalWrite(LED_BUILTIN, HIGH);
      delay(3000);
      // digitalWrite(powder, LOW)
      digitalWrite(LED_BUILTIN, LOW);
      delay(3000);
    }
    else {
      for (int i = 0; i < 12; i++){
        digitalWrite(LED_BUILTIN, HIGH);
        delay(100);
        digitalWrite(LED_BUILTIN, LOW);
        delay(100);
      }
    }
  }
}

