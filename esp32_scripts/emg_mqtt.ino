// Leer sensor EMG y envia mediante MQTT
#include "config.h" // archivo de configuracion del protocolo MQTT

#define PIN_FLEXION 32 //Se puede modificar
#define PIN_EXTENSION 26 //Se puede modificar
#define DELAY 50 // Freq: 20Hz (Se puede modificar)

// State of connection variables
bool internetOk = false;
bool brokerOk = false;
bool sensorOk = false;
// Declaration of the client objects
WiFiClientSecure ClientEsp;
PubSubClient client(ClientEsp);
// global variables read by the sensor
static float data = 0;
// data used in the callback 
String _topic;
String _payload;
// sensor GPIO signal 
const int PIN_SIGNAL = 25;
  
// Variables asignadas a los datos sacados del ADC y a sus voltajes
static unsigned int data_extension = 0;
static unsigned int data_flexion = 0;
static unsigned float = v_extension = 0.0;
static unsigned float = v_flexion = 0.0;

// Función para leer y computar el valor de los sensores
void readSensor(unsigned int delay_enviado){

  //Lectura análogica de los sensores mioeléctricos
  data_extension = analogRead(PIN_EXTENSION);
  data_flexion = analogRead(PIN_FLEXION);

  //Conversión de los valores de ADC a voltaje eléctrico
  v_extension = (unsigned float)data_extension*(3.3/4095);
  v_flexion = (unsigned float)data_flexion*(3.3/4095);
  
  delay(delay_enviado);
}
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
// DO NOT MODIFY: function to connect to the HiveMQ broker
void connectMQTT(){
  while (!client.connected()){
    if (client.connect("ESP32Client", mqtt_username, mqtt_password)){
      brokerOk = true;
    } else{ // connection failure
      Serial.print("Failure, state = ");
      Serial.println(client.state());
      delay(5000); 
    }
  }
}
// DO NOT MODIFY: function to send the callback to the broker
void callback(char* topic, byte* payload, unsigned int length){
  String conc_payload_;
  for (int i=0;i<length;i++){
    conc_payload_ +=(char)payload[i];
  }
  _topic=topic;
  _payload=conc_payload_;
}

void setup(){
  ClientEsp.setCACert(root_ca);  // Set the root certificate
  Serial.begin(115200);
  // Configure WiFi, MQTT broker direction and callback
  wificonf();
  client.setServer(server_mqtt,puerto_mqtt);
  client.setCallback(callback);
}

void loop(){
  
  // Conexión al cliente
  if (!client.connected()){
    connectMQTT();
  }
  client.loop();

  readSensor(DELAY); //Lee los valores de los sensores con un "delay" determinado 
  
  //Publicar los datos de voltaje en la nube
  if(not isnan(v_flexion) or v_flexion == 0){
    client.publish("/emg/flexion", String(v_flexion).c_str());
  }
  if(not isnan(v_extension) or v_extension == 0){
    client.publish("/emg/extension", String(v_extension).c_str());
  }
}
