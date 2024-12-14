"""
Archivo para leer los datos de .csv y enviarlo al servidor MQTT
"""
#!/usr/bin/env python
import os
import glob
import paho.mqtt.client as mqtt
import warnings
import time
import pandas as pd

warnings.filterwarnings("ignore", category=DeprecationWarning)

# frecuencia de publicacion / lectura datos
FREQ_PUB = 4  # Hz

# Class to publish data to the broker HiveMQ
class Publisher:
    """
    CLASS VARIABLES
    """
    # USER, PASSWORD config
    USER = "server_1"
    PW = "Servicios25"
    # broker HiveMQ and port
    server_mqtt = "3c8bafd418db43cca27124589b10b2d8.s1.eu.hivemq.cloud"
    puerto_mqtt = 8883
    # tiempo max espera
    MAX_TIMEOUT = 30  # secs
    # csv path and files
    DATA_CSV_DIR = os.path.join(os.getcwd(), "csv")
    DATA_FILES = [os.path.join(DATA_CSV_DIR, f) for f in os.listdir(DATA_CSV_DIR) if f.endswith('.csv')]

    """
    CLASS CONSTRUCTOR
    """
    def __init__(self, server, port, username=USER, password=PW):
        self.client = mqtt.Client()  # Client MQTT
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)  # Configure TLS
        self.setUser(username, password)
        self.server = server
        self.port = port
        self.connected = False  # Connection state
        self.client.on_connect = self._on_connect  # Connection callback

    """
    INSTANCE METHODS & CALLBACKS
    """
    def _on_connect(self, _, __, ___, rc):
        if rc == 0:
            print("Connected to HiveMQ broker")
            self.connected = True
        else:
            print("Error:", rc)
            self.connected = False

    def setUser(self, user, pw):
        self.client.username_pw_set(user, pw)

    def connect(self):
        print("Trying to connect to the broker...")
        self.client.connect(self.server, self.port)
        self.client.loop_start()
        print("Successfully connected!")
        # Esperar hasta que se conecte
        start_time = time.time()
        while not self.connected:
            if time.time() - start_time > self.MAX_TIMEOUT:
                print("Wait time over")
                self.client.loop_stop()
                return False
            time.sleep(0.1)
        return True

    def publish(self, topic, message):
        if self.connected:
            self.client.publish(topic, message)
        else:
            print("Could not publish, not connected to the broker.")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from broker.")

"""
MAIN PROGRAM
"""
if __name__ == "__main__":
    # Leer el archivo CSV
    csv_file = Publisher.DATA_FILES[0]  # Change the index based on the required file
    data = pd.read_csv(csv_file)  # datos del .csv

    # Crear un objeto Publisher y conectarse al broker
    pub = Publisher(Publisher.server_mqtt, Publisher.puerto_mqtt, "esp32_emg", "Servicios25")
    if pub.connect():
        # Iterar sobre los datos y publicarlos
        for _, row in data.iterrows():
            pub.publish("/timestamp", row["Tiempo"])
            pub.publish("/emg/flexion", row["V_flexion"])
            pub.publish("/emg/extension", row["V_extension"])
            pub.publish("/imu/j4", row["Col_4"])
            pub.publish("/imu/j5", row["Col_5"])
            pub.publish("/button", 0)
            time.sleep(1.0 / FREQ_PUB)  # intervalo entre publicaciones
        # fin de la simulacion 
        for i in range(5):
            pub.publish("/button", 1)
        # Desconectar al finalizar
        pub.disconnect()
