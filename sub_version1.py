# hacer !pip install paho-mqtt en tu entorno previamente
import paho.mqtt.client as mqtt
# Configuración del broker HiveMQ y del puerto seguro
server_mqtt = "3c8bafd418db43cca27124589b10b2d8.s1.eu.hivemq.cloud"
puerto_mqtt = 8883
topic = "/emg"
# configuracion del username y la password para acceder al broker
username = "JuanPerez"
password = "servicios2025"
# Funciones de callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT!")
        client.subscribe(topic)
        print(f"Suscrito al topic '{topic}'")
    else:
        print("Error al conectar, código de error:", rc)

def on_message(client, userdata, msg):
    print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}")

# Creación del cliente MQTT
client = mqtt.Client()

# Configuración de TLS para conexión segura
client.tls_set()  # Utiliza la configuración predeterminada de TLS
client.username_pw_set(username, password)  # Sustituye con tu usuario y contraseña

# Configuración de callbacks
client.on_connect = on_connect
client.on_message = on_message

# Conexión al broker y loop
client.connect(server_mqtt, puerto_mqtt)
client.loop_forever()
