import paho.mqtt.client as mqtt
import warnings
import time

warnings.filterwarnings("ignore", category=DeprecationWarning)


# Class to subscribe to the broker HiveMQ
class Subscriber:
    """
    CLASS VARIABLES
    """
    # USER, PASSWORD config
    USER = "user1"
    PW = "Srv2025"
    # broker HiveMQ and port
    server_mqtt = "3c8bafd418db43cca27124589b10b2d8.s1.eu.hivemq.cloud"
    puerto_mqtt = 8883
    MAX_TIMEOUT = 30 # 30 secs de timeout to stop reading from broker

    """
    CLASS CONSTRUCTOR
    """
    # Constructor using server, port, username, pw
    def __init__(self, server, port, username=USER, password=PW):
        self.client = mqtt.Client()  # Client MQTT
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)  # Configure TLS
        self.setUser(username, password) 
        self.server = server
        self.port = port
        self.topic = ""
        self.connected = False  # connection state
        self.msg = None  # last msg received
        self.client.on_connect = self._on_connect  # connection callback
        self.client.on_message = self._on_message  # msg callback

    """
    INSTANCE METHODS & CALLBACKS
    """
    # connection callback
    def _on_connect(self, _, __, ___, rc):
        if rc == 0:
            print("Conexion al broker MQTT exitosa")
            self.client.subscribe(self.topic)
            self.connected = True
        else:
            print("Error en la conexion, codigo de error:", rc)
            self.connected = False

    # message callback
    def _on_message(self, _, __, msg):
        self.msg = msg.payload.decode()

    def setUser(self, user, pw):
        self.client.username_pw_set(user, pw)
     
    # set the topic string to subscribe from
    def setTopic(self, topic):
        self.topic = topic

    # verify broker connection
    def checkTopic(self):
        print("Intentando conectar al broker...")
        self.client.connect(self.server, self.port)
        self.client.loop_start()
        
        # wait using a MAX_TIMEOUT
        start_time = time.time()
        while not self.connected:
            if time.time() - start_time > self.MAX_TIMEOUT:
                print("Tiempo de espera agotado para la conexion.")
                self.client.loop_stop()
                return False
            time.sleep(0.1)  # Espera breve antes de verificar nuevamente
        
        return self.connected

    # get the topic message
    def getMsg(self):
        if self.checkTopic():   
            start_time = time.time()
            while self.msg is None:
                if time.time() - start_time > self.MAX_TIMEOUT:  
                    print("Tiempo de espera agotado para recibir el mensaje.")
                    return None
                if self.msg is not None:
                    time.sleep(0.1)  # Espera breve antes de verificar nuevamente
            return self.msg
        return None  # cannot connect to broker or simply topic does not exist
"""
if __name__ == "__main__":
    topic = "/emg"
    while True:
        sub = Subscriber(server_mqtt, puerto_mqtt, USER, PW)
        sub.setTopic(topic)
        msg = sub.getMsg()
        print(f"Mensaje recibido del topic '{topic}': {msg}")
        if msg is None:
            break
"""
