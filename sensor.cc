//#include <Arduino.h>

const int myowarePin = 36; // Pin analógico al que está conectado el sensor MyoWare

void setup() {
    Serial.begin(115200);
    delay(1000);
}

void loop() {
    int sensorValue = analogRead(myowarePin);
    Serial.print("Valor del sensor MyoWare: ");
    Serial.println(sensorValue);
    delay(100);
}
