#include <Wire.h>
#include <LIS3MDL.h>
#include <LSM6.h>
#include "config.h" // Archivo de configuración para WiFi y MQTT

// Pines
#define BUTTON_PIN 23 // GPIO del botón
// Frecuencia de publicación
#define PUBLISH_INTERVAL 500

#define PIN_FLEXION 32 //Se puede modificar
#define PIN_EXTENSION 25 //Se puede modificar
#define DELAY 50 // Freq: 20Hz (Se puede modificar)

// State of connection variables
bool internetOk = false;
bool brokerOk = false;
bool sensorOk = false;

static float data = 0;
// data used in the callback 
// sensor GPIO signal 
const int PIN_SIGNAL = 25;
  
// Variables asignadas a los datos sacados del ADC y a sus voltajes
static unsigned int data_extension = 0;
static unsigned int data_flexion = 0;
static float v_extension = 0.0;
static float v_flexion = 0.0;


// Clase para gestionar la IMU
class IMUHandler {
private:
    LIS3MDL mag;    // Magnetómetro
    LSM6 imu;       // Acelerómetro y Giroscopio

    float accel_ang_x = 0.0, accel_ang_y = 0.0;
    float ang_x = 0.0, ang_y = 0.0;
    float ang_x_prev = 0.0, ang_y_prev = 0.0;
    float roll_offset = 0.0, pitch_offset = 0.0;
    bool offsets_calculados = false;
    unsigned long tiempo_prev;

    // Determina el estado de un ángulo
    

public:
    IMUHandler() {}

    void init() {
        // Inicializar sensores
        Wire.begin();

        if (!mag.init()) {
            Serial.println("No se detectó el magnetómetro LIS3MDL");
            while (1);
        }
        mag.enableDefault();

        if (!imu.init()) {
            Serial.println("No se detectó el IMU LSM6");
            while (1);
        }
        imu.enableDefault();

        tiempo_prev = millis();
    }
    int determineState(float angle) {
        if (angle > 40) return 1;
        if (angle < -40) return 2;
        return 0;
    }

    void updateAngles() {
        imu.read();

        // Calcular el delta de tiempo
        unsigned long currentTime = millis();
        float dt = (currentTime - tiempo_prev) / 1000.0;
        tiempo_prev = currentTime;

        // Calcular ángulos de roll y pitch con acelerómetro
        accel_ang_x = atan2(imu.a.y, imu.a.z) * (180.0 / PI); // Roll
        accel_ang_y = atan2(-imu.a.x, sqrt(imu.a.y * imu.a.y + imu.a.z * imu.a.z)) * (180.0 / PI); // Pitch

        // Aplicar el filtro complementario
        ang_x = 0.98 * (ang_x_prev + (imu.g.x / 131.0) * dt) + 0.02 * accel_ang_x; // Roll
        ang_y = 0.98 * (ang_y_prev + (imu.g.y / 131.0) * dt) + 0.02 * accel_ang_y; // Pitch

        ang_x_prev = ang_x;
        ang_y_prev = ang_y;

        // Calcular offsets iniciales
        if (!offsets_calculados) {
            roll_offset = ang_x;
            pitch_offset = ang_y;
            offsets_calculados = true;
        }

        // Ajustar referencia
        ang_x -= roll_offset;
        ang_y -= pitch_offset;

        // Normalizar ángulos a rango -180 a 180
        if (ang_x > 180) ang_x -= 360;
        if (ang_x < -180) ang_x += 360;
        if (ang_y > 180) ang_y -= 360;
        if (ang_y < -180) ang_y += 360;
    }

    int getRollState() {
        return determineState(ang_x);
    }

    int getPitchState() {
        return determineState(ang_y);
    }

    void printStates() {
        Serial.print("Roll: ");
        Serial.print(ang_x);
        Serial.print("°, Pitch: ");
        Serial.println(ang_y);
    }
};

// Objeto global para manejar la IMU
IMUHandler imuHandler;

// WiFi y MQTT


WiFiClientSecure espClient; // ERROR CORREGIDO: NO puede ser WiFiClient
PubSubClient client(espClient);
// data used in the callback from mqtt 
String _topic;
String _payload;

//FUNCION
void readSensor1(unsigned int delay_enviado){

  //Lectura análogica de los sensores mioeléctricos
  data_extension = analogRead(33);
  v_extension = (float)data_extension*(3.3/4095);
  
  Serial.print("V_extension: ");
  Serial.println(v_extension);
 
  
  delay(delay_enviado);
}

void readSensor2(unsigned int delay_enviado){

 
  data_flexion = analogRead(32);

  //Conversión de los valores de ADC a voltaje eléctrico
  
  v_flexion = (float)data_flexion*(3.3/4095);
 
  Serial.print("V_flexion: ");
  Serial.println(v_flexion);
  
  delay(delay_enviado);
}

// Función para configurar la conexión WiFi
// DO NOT MODIFY: function to connect to the WiFi
void wificonf(){
  delay(10);
  WiFi.begin(ssid,password);
  while (WiFi.status() != WL_CONNECTED){
    delay(1000);
  }
  internetOk = true;
  delay(500);
}

// Función para conectar al broker MQTT
void connectMQTT() {
    client.setKeepAlive(60);
    while (!client.connected()) {
        if (client.connect("ESP32Client", mqtt_username, mqtt_password)) {
            Serial.println("Conectado al broker MQTT.");
        } else {
            Serial.print("Fallo al conectar, estado: ");
            Serial.println(client.state());
            delay(5000);
        }
    }
}
// callback para manejar el msg.payload del mqtt 
void callback(char* topic, byte* payload, unsigned int length){
  String conc_payload_;
  for (int i=0;i<length;i++){
    conc_payload_ +=(char)payload[i];
  }
  _topic=topic;
  _payload=conc_payload_;
}
// Publicar datos a la nube
void publishData(int rollState, int pitchState, bool buttonPressed) {
    client.publish("/imu/j4", String(rollState).c_str());
    client.publish("/imu/j5", String(pitchState).c_str());
    client.publish("/button", !buttonPressed ? "0" : "1");
/*
    Serial.print("Roll State: ");
    Serial.print(rollState);
    Serial.print(", Pitch State: ");
    Serial.print(pitchState);
    Serial.print(", Button: ");
    Serial.println(buttonPressed ? "Pressed" : "Not Pressed");
*/
}

void setup() {
    Serial.begin(115200);
    espClient.setCACert(root_ca);  // ERROR CORREGIDO: Set the root certificate
    // Configurar WiFi y MQTT
    wificonf();
    client.setServer(server_mqtt, puerto_mqtt);
    client.setCallback(callback); // ERROR CORREGIDO: Se necesita un callback para enviar el msg.payload asociado a un topic
    // Inicializar sensores y botón
    imuHandler.init();
    pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
    if (!client.connected()) {
        connectMQTT();
    }
    client.loop();


    readSensor1(DELAY); //Lee los valores de los sensores con un "delay" determinado 
    readSensor2(DELAY);

    if(not isnan(v_flexion) or v_flexion == 0){
      client.publish("/emg/flexion", String(v_flexion).c_str());
    }
    if(not isnan(v_extension) or v_extension == 0){
      client.publish("/emg/extension", String(v_extension).c_str());
    }
    // Actualizar ángulos de la IMU
    
    imuHandler.updateAngles();

    // Leer estado del botón
    bool buttonPressed = digitalRead(BUTTON_PIN) == LOW;

    // Publicar datos a la nube cada 500 ms
    static unsigned long lastPublishTime = 0;
    if (millis() - lastPublishTime >= PUBLISH_INTERVAL) {
        lastPublishTime = millis();

        int rollState = imuHandler.getRollState(); // Las variables a enviar al broker las haría tipo "static"
        int pitchState = imuHandler.getPitchState();

        publishData(rollState, pitchState, buttonPressed);
    }
}
