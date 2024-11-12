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
        FLEX_TOPIC = flex_topic
        EXT_TOPIC = ext_topic
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
    METODOS DE INSTANCIA
    """
    def read_mqtt(self):
        # instancia de los subscriptores a los topics de flexion y extension
        sub_flex = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt, Subscriber.USER, Subscriber.PW)
        sub_ext = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt, Subscriber.USER, Subscriber.PW)
        
        # establecer el topic de subscripcion
        sub_flex.setTopic(FLEX_TOPIC)
        sub_ext.setTopic(EXT_TOPIC)

        # guardar el valor leido por los topics en los atributos
        self.setFlex(sub_flex.getMsg())
        self.setExt(sub_ext.getMsg())

    """
    METODOS DE CLASE
    """
    @classmethod
    def assign_action(cls, emgObj): # emgObj is an object of type Emg
        # read from the mqtt
        emgObj.read_mqtt()
        # get the instance's flexion and extension values
        flex = emgObj.getFlex()
        ext = emgObj.getExt()
        threshold = emgObj.getUmbral()
        # clasificar la accion
        if flex < threshold and ext < threshold: # doble activacion muscular
            emgObj.setAction(Action.COCONTRACCION)
        
        elif flex < threshold and ext >= threshold:
            emgObj.setAction(Action.FLEXION)  # Solo flexión activa
 
        elif ext < threshold and flex >= threshold:
            emgObj.setAction(Action.EXTENSION)  # Solo extensión activa
        
        else:
            emgObj.setAction(Action.REPOSO)  # Ambas señales inactivas, reposo

"""
Uso
 -> inicializar objeto tipo Emg y despues leer en un while True
   emgObj = Emg("/emg/flex", "/emg/ext")
   while True:
       emgObj.read_mqtt()
       Emg.assign_action(emgObj)
       accion = emgObj.getAction()
       # if accion == Action.COCONTRACCION then cambiar de articulacion
"""
