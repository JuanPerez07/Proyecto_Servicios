#include "config.h" // archivo de configuracion del protocolo MQTT

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
// function to read values from the sensor each 5 seconds
void readSensor(){
  data = analogRead(PIN_SIGNAL); // read analog value
  if (isnan(data)) {
    sensorOk = false;
  } else {
    sensorOk = true;
  }
  delay(5000);
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
  // client connection
  if (!client.connected()){
    connectMQTT();
  }
  client.loop();
  //readSensor(); // reads values to send to the broker
  data = random(0, 351);
  delay(5000);
  //--------------------------------------------------------------------------
  // publish to the broker in the cloud
  if(not isnan(data)){
    client.publish("/emg", String(data).c_str());
  }
}