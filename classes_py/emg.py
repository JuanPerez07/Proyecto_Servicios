"""
Clase emg
	Atributos:
           - action (tipo enum de las acciones posibles)
	   - flex y ext (acciones flexion/extension segun canales EMG) 
	   - umbral (umbral para distinguir accion ON/OFF)
           - cadenas string de los topics como variables de clase
	Metodos:
           - getActions (devuelve las acciones posibles)
           - getStatus(devuelve la accion leida de los topics del sensor)
           - getUmbral (devuelve el umbral ON/Off de las acciones)
           - setUmbral (establece el umbral de las acciones on/off)

"""
from subscriber import Subscriber # class import
from enum import Enum # tipo enumerado
# clase Action -> tipo enumerado de las acciones que habra en la fsm de emgState
class Action(Enum):
    REPOSO = 1
    FLEXION = 2
    EXTENSION = 3
    COCONTRACCION = 4
# clase Emg
class Emg:
    # constructor a partir de los topics de flexion y extension y umbral default a 2 Voltios
    def __init__(self, flex_topic, ext_topic, umbral=2):
        # variables de instancia
        self.umbral = umbral # umbral ON/OFF
        self.ext = 0 # inicializar a valores invalidos
        self.flex = 0
        self.action = Action.REPOSO # inicialmente reposo
        # variables de clase
        Emg.FLEX_TOPIC = flex_topic
        Emg.EXT_TOPIC = ext_topic
    """
    SETTERS
    """
    def setFlex(self, flex):
        self.flex = flex

    def setExt(self, ext):
        self.ext = ext
    
    def setUmbral(self, umbral):
        self.umbral = umbral

    def setAction(self, action):
        self.action = action

    """
    GETTERS    
    """
    def getFlex(self):
        return self.flex

    def getExt(self):
        return self.ext
    
    def getUmbral(self):
        return self.umbral

    def getAction(self):
        return self.action

    """
    METODOS DE CLASE
    """
    @classmethod
    def read_is_valid(cls, flex_value, ext_value): # comprueba que la lectura es valida
        return flex_value is not None and flex_value > 0 and ext_value is not None and ext_value > 0

    """
    METODOS DE INSTANCIA
    """
    # metodo para establecer los valores leidos de los topics de /emg
    def read_mqtt(self):
        # instancia de los subscriptores a los topics de flexion y extension
        sub_flex = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt)
        sub_ext = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt)
        
        # establecer el topic de subscripcion
        sub_flex.setTopic(Emg.FLEX_TOPIC)
        sub_ext.setTopic(Emg.EXT_TOPIC)

        # guardar el valor leido por los topics en los atributos
        self.setFlex(sub_flex.getMsg())
        self.setExt(sub_ext.getMsg())        

    # metodo para asignar la action segun las lecturas emg de los sensores
    def assign_action(self, read_broker=True): # bool parameter to read broker, by default True
        # read from the mqtt
        if read_broker:
            self.read_mqtt()
        # get the instance's flexion and extension values
        flex = self.getFlex()
        ext = self.getExt()
        threshold = self.getUmbral()
        # clasificar la accion si la lectura es valida (mayor que cero y diferente de None)
        if Emg.read_is_valid(flex, ext):
            if flex < threshold and ext < threshold: # doble activacion muscular
                self.setAction(Action.COCONTRACCION)
        
            elif flex < threshold and ext >= threshold:
                self.setAction(Action.FLEXION)  # Solo flexión activa
 
            elif ext < threshold and flex >= threshold:
                self.setAction(Action.EXTENSION)  # Solo extensión activa
        
            else:
                self.setAction(Action.REPOSO)  # Ambas señales inactivas, reposo

"""
Uso
 -> inicializar objeto tipo Emg con los topics a leer y despues leer en un while True
   emgObj = Emg("/emg/flex", "/emg/ext")
   while True:
       emgObj.assign_action()
       accion = emgObj.getAction()
       # if accion == Action.COCONTRACCION then cambiar de articulacion

Ejemplo sin conexion a MQTT
# objeto tipo emg
emgObj =  Emg("/emg/flex","/emg/ext")
# simular data adquirida
emgObj.setFlex(1.2) # flexion detectada 
emgObj.setExt(1.1) # extension detectada
emgObj.assign_action(False) # prueba sin conexion a mqtt de la logica de acciones
print(emgObj.getAction())
"""
