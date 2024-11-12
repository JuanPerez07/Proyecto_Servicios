import paho.mqtt.client as mqtt
import warnings
import time

warnings.filterwarnings("ignore", category=DeprecationWarning)


# Clase para suscribirse a un topic en el broker MQTT
class Subscriber:
    """
    VARIABLES DE CLASE (no hacen falta instancias de la clase para acceder a ellas)
    """
    # Configuración del usuario y contraseña del broker
    USER = "JuanPerez"
    PW = "servicios2025"
    # Configuración del broker HiveMQ y del puerto seguro
    server_mqtt = "3c8bafd418db43cca27124589b10b2d8.s1.eu.hivemq.cloud"
    puerto_mqtt = 8883
    MAX_TIMEOUT = 30 # 30 segundos de timeout para detener lectura de mqtt si no recibe nada

    """
    CONSTRUCTOR DE CLASE
    """
    # Constructor con servidor, puerto, usuario y contraseña
    def __init__(self, server, port, username=USER, password=PW):
        self.client = mqtt.Client()  # Cliente MQTT
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)  # Configurar TLS de manera explícita
        self.setUser(username, password)  # Configurar usuario y contraseña
        self.server = server
        self.port = port
        self.topic = ""
        self.connected = False  # Estado de conexión
        self.msg = None  # Último mensaje recibido
        self.client.on_connect = self._on_connect  # Callback para manejar conexión
        self.client.on_message = self._on_message  # Callback para manejar mensajes

    """
    METODOS DE INSTANCIA Y CALLBACKS
    """
    # Método interno para manejar la conexión
    def _on_connect(self, _, __, ___, rc):
        if rc == 0:
            print("Conexión al broker MQTT exitosa")
            self.client.subscribe(self.topic)
            self.connected = True
        else:
            print("Error en la conexión, código de error:", rc)
            self.connected = False

    # Método interno para manejar mensajes
    def _on_message(self, _, __, msg):
        self.msg = msg.payload.decode()

    # Configura el usuario y contraseña
    def setUser(self, user, pw):
        self.client.username_pw_set(user, pw)
     
    # Configura el topic
    def setTopic(self, topic):
        self.topic = topic

    # Verifica la conexión al broker y suscripción al topic
    def checkTopic(self):
        print("Intentando conectar al broker...")
        self.client.connect(self.server, self.port)
        self.client.loop_start()
        
        # Espera con límite de tiempo para establecer conexión
        start_time = time.time()
        while not self.connected:
            if time.time() - start_time > MAX_TIMEOUT: # Tiempo de espera max para conectar al broker
                print("Tiempo de espera agotado para la conexión.")
                self.client.loop_stop()
                return False
            time.sleep(0.1)  # Espera breve antes de verificar nuevamente
        
        return self.connected

    # Obtiene el mensaje del topic
    def getMsg(self):
        if self.checkTopic():  # Verifica conexión y suscripción al topic 
            # Espera a recibir un mensaje
            start_time = time.time()
            while self.msg is None:
                if time.time() - start_time > MAX_TIMEOUT:  # Tiempo de espera max. para recibir mensaje
                    print("Tiempo de espera agotado para recibir el mensaje.")
                    return None
                if self.msg is not None:
                    time.sleep(0.1)  # Espera breve antes de verificar nuevamente
            return self.msg
        return None  # En caso de que no haya conexión al broker o exista el topic
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
