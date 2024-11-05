# hacer !pip install paho-mqtt en tu entorno previamente
import paho.mqtt.client as mqtt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Configuración del broker HiveMQ y del puerto seguro
server_mqtt = "3c8bafd418db43cca27124589b10b2d8.s1.eu.hivemq.cloud"
puerto_mqtt = 8883
# This class will sub to the cloud broker topics to retrieve data from sensor
class Subscriber:
    # constructor from server,port, user and pw
    def __init__(self, server, port, username, password):
        self.client = mqtt.Client() # client MQTT
        self.client.tls_set() # config TLS for secure connection
        self.setUser(username, password) # set the verified user of the broker
        self.server = server
        self.port = port
        self.topic = " "
        self.connected = False # variable to check the connection to the broker
        self.msg = None # variable to store the last msg received from the topic
        self.client.on_connect = self._on_connect # callback para regular conexion
        self.client.on_message = self._on_message # callback para obtener el mensaje
    
    # metodo interno para manejar conexion
    def _on_connect(self, _, __, rc): # rc es un codigo de error
        if rc == 0: # no error
            print("Conexion al broker MQTT exitosa")
            self.client.subscribe(self.topic)    
            self.connected = True
        else:
            self.connected = False
            print("Error en la conexión, código de error: ", rc)
    
    # método interno para manejar mensajes
    def _on_message(self, _, __, msg):
        #print(f"Msg recibido en {msg.topic}: {msg.payload.decode()}")
        self.msg = msg.payload.decode()

    # set the username and pw
    def setUser(self, user, pw):
        self.client.username_pw_set(user, pw)
     
    # set the topic to subscribe from
    def setTopic(self, topic):
        self.topic = topic

    # chekea conexion al broker y subscripcion al topic
    def checkTopic(self):
        print("checking connection to topic and broker...")        
        self.client.connect(self.server, self.port)
        self.client.loop_start() # inicia loop MQTT 
        while not self.connected:
            pass # wait until succesfully connected to the broker
        return self.connected

    # getter del contenido del topic
    def getMsg(self):
        if self.checkTopic(): # verifica conexion y subscripcion al topic 
           # espera a recibir un mensaje
           while self.msg is None:
               pass
           return self.msg
        return None # en caso de que no haya conexion / exista el topic


"""
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

# Configuración de callbacks
client.on_connect = on_connect
client.on_message = on_message
"""
if __name__ == "__main__":
    topic = "/emg"
    sub = Subscriber(server_mqtt, puerto_mqtt, "username", "password")
    sub.setTopic(topic)
    msg = sub.getMsg()
    print(f"Mensaje recibido del topic '{topic}': {msg}")
