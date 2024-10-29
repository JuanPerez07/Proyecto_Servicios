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
/*
#define SAMPLES 100
#define SENSOR_PIN 34  // Pin analógico para leer del sensor

// Función para obtener los datos del sensor (simulando con una lectura analógica)
float getSensorData() {
    int analogValue = analogRead(SENSOR_PIN);  // Lee el valor del sensor
    return (analogValue / 4095.0) * 3.3;       // Convierte el valor a voltaje (0 - 3.3V)
}

void setup() {
    Serial.begin(115200);  // Inicializa la comunicación serial
    delay(1000);           // Espera un momento para la inicialización de Serial

    // Imprime encabezados para el CSV
    Serial.println("Muestra,Valor del Sensor");
}

void loop() {
    for (int j = 0; j < SAMPLES; ++j) {
        float sensorValue = getSensorData();  // Lee el sensor
        Serial.print(j);                      // Muestra el índice de la muestra
        Serial.print(",");
        Serial.println(sensorValue);          // Muestra el valor del sensor

        delay(100);  // Espera entre muestras
    }

    // Termina el bucle después de capturar las muestras
    while (true) {
        delay(1000);
    }
}

*/
