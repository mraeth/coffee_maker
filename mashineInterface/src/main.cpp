#include <Arduino.h>
#include <SoftwareSerial.h>

#define LED_PIN LED_BUILTIN

#define SSD_PIN 2
#define RELAY_PIN 3 

SoftwareSerial btSerial(5, 4); // Arduino RX=5, TX=4

void setup() {
  pinMode(SSD_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  Serial.begin(9600);
  btSerial.begin(9600);
}

void loop() {
  if (btSerial.available() >= 2) {
    char cmd = btSerial.read();
    char val = btSerial.read();
    if (cmd == 'H') {
      digitalWrite(SSD_PIN, val == '1' ? HIGH : LOW);
    } else if (cmd == 'P') {
      digitalWrite(RELAY_PIN, val == '1' ? HIGH : LOW);
    }
  }
}

