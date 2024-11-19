//Pines del sensor
//gnd -> gnd
//SCL -> g22
//SDA -> g21
//vin -> 3.3v

//quitar ek yaw de la implementacion.

#include <Wire.h>
#include <LIS3MDL.h>
#include <LSM6.h>

class IMUSensor {
private:
  LIS3MDL mag;    // Magnetómetro
  LSM6 imu;       // Acelerómetro y Giroscopio

  // Variables para los ángulos
  float accel_ang_x = 0.0;
  float accel_ang_y = 0.0;
  float girosc_ang_x = 0.0;
  float girosc_ang_y = 0.0;

  float ang_x = 0.0, ang_y = 0.0;
  float ang_x_prev = 0.0, ang_y_prev = 0.0;

  unsigned long tiempo_prev;

  // Offsets para roll y pitch
  float roll_offset = 0.0;
  float pitch_offset = 0.0;

  // Indica si los offsets iniciales ya fueron calculados
  bool offsets_calculados = false;

  // GPIO del botón
  const int buttonPin = 23;

public:
  // Método para inicializar los sensores y configurar el botón
  void init() {
    Serial.begin(115200);
    Wire.begin();

    // Configurar pin del botón como entrada con pull-up
    pinMode(buttonPin, INPUT_PULLUP);

    // Inicializar el magnetómetro
    if (!mag.init()) {
      Serial.println("No se detectó el magnetómetro LIS3MDL");
      while (1);
    }
    mag.enableDefault();

    // Inicializar el acelerómetro y giroscopio
    if (!imu.init()) {
      Serial.println("No se detectó el IMU LSM6");
      while (1);
    }
    imu.enableDefault();

    // Inicializar tiempo para integración del giroscopio
    tiempo_prev = millis();
  }

  // Método para actualizar y calcular los ángulos
  void update() {
    // Leer datos del acelerómetro y giroscopio
    imu.read();

    // Calcular el delta de tiempo
    unsigned long currentTime = millis();
    float dt = (currentTime - tiempo_prev) / 1000.0; // delta de tiempo en segundos
    tiempo_prev = currentTime;

    // Calcular ángulo de roll y pitch usando el acelerómetro
    accel_ang_x = atan2(imu.a.y, imu.a.z) * (180.0 / PI); // Roll
    accel_ang_y = atan2(-imu.a.x, sqrt(imu.a.y * imu.a.y + imu.a.z * imu.a.z)) * (180.0 / PI); // Pitch

    // Integrar velocidades angulares del giroscopio para obtener ángulos (Roll y Pitch)
    girosc_ang_x += (imu.g.x * dt) / 131.0;  // Roll (en grados)
    girosc_ang_y += (imu.g.y * dt) / 131.0;  // Pitch (en grados)

    // Aplicar el filtro complementario
    ang_x = 0.98 * (ang_x_prev + (imu.g.x / 131.0) * dt) + 0.02 * accel_ang_x; // Roll
    ang_y = 0.98 * (ang_y_prev + (imu.g.y / 131.0) * dt) + 0.02 * accel_ang_y; // Pitch

    // Actualizar valores previos
    ang_x_prev = ang_x;
    ang_y_prev = ang_y;

    // Calcular offsets iniciales para establecer como referencia el punto de inicio
    if (!offsets_calculados) {
      roll_offset = ang_x;
      pitch_offset = ang_y;
      offsets_calculados = true;
    }

    // Ajustar roll y pitch para mantenerlos en el rango de -180 a 180
    ang_x -= roll_offset;
    ang_y -= pitch_offset;

    if (ang_x > 180) ang_x -= 360;
    if (ang_x < -180) ang_x += 360;
    if (ang_y > 180) ang_y -= 360;
    if (ang_y < -180) ang_y += 360;
  }

  // Método para imprimir los valores de los ángulos y el estado del botón
  void printAnglesAndButton() {
    static unsigned long lastPrintTime = 0;
    bool buttonPressed = digitalRead(buttonPin);

    // Imprimir los ángulos en el monitor serial cada 500 ms
    if (millis() - lastPrintTime >= 500) {
      lastPrintTime = millis();

      // Leer el estado del botón (inverso porque está en pull-up)

      // Redondear ángulos a múltiplos de 10
      int ang_x_rounded = round(ang_x / 10) * 10;
      int ang_y_rounded = round(ang_y / 10) * 10;

      Serial.print("Roll: ");
      Serial.print(ang_x_rounded);
      Serial.print("°, Pitch: ");
      Serial.print(ang_y_rounded);
      Serial.print("°, Button: ");
      Serial.println(!buttonPressed ? "Pressed" : "Not Pressed");
    }
  }
};

// Instancia de la clase
IMUSensor imuSensor;

void setup() {
  imuSensor.init(); // Inicializar el sensor y el botón
}

void loop() {
  imuSensor.update();             // Actualizar los cálculos
  imuSensor.printAnglesAndButton(); // Imprimir ángulos y estado del botón
}
