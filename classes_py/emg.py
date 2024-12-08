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
from classes_py.subscriber import Subscriber
#from subscriber import Subscriber # class import
from enum import Enum # enum type
# class Action -> encode actions based on emg signals
class EmgAction(Enum):
    REPOSO = 1
    FLEXION = 2
    EXTENSION = 3
    COCONTRACCION = 4
# class Emg
class Emg:
    # Constructor based on topic names and umbral default a 2 Voltios
    def __init__(self, flex_topic, ext_topic, umbral=2.0):
        # instance variables
        self.umbral = float(umbral) # umbral ON/OFF
        self.ext = 0
        self.flex = 0
        self.action = EmgAction.REPOSO
        # class variables
        Emg.FLEX_TOPIC = flex_topic
        Emg.EXT_TOPIC = ext_topic
    """
    SETTERS
    """
    def setFlex(self, flex):
        self.flex = float(flex)

    def setExt(self, ext):
        self.ext = float(ext)
    
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
    CLASS METHOD
    """
    @classmethod
    def read_is_valid(cls, flex_value, ext_value): 
        return flex_value is not None and flex_value > 0 and ext_value is not None and ext_value > 0

    """
    INSTANCE METHODS
    """
    # set the flex and ext values read from topic /emg
    def read_mqtt(self):
        # instance Subscriber objects to read topics /emg/flexion and /emg/extension
        sub_flex = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt)
        sub_ext = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt)
        
        # set the topic names
        sub_flex.setTopic(Emg.FLEX_TOPIC)
        sub_ext.setTopic(Emg.EXT_TOPIC)

        # save values read from the broker
        self.setFlex(sub_flex.getMsg())
        self.setExt(sub_ext.getMsg())        

    def assign_action(self, read_broker=True): # bool parameter to read broker, by default True
        # read from the mqtt
        if read_broker:
            self.read_mqtt()
        # get the instance's flexion and extension values
        flex = self.getFlex()
        ext = self.getExt()
        threshold = self.getUmbral()
        # classify action if read is valid
        if Emg.read_is_valid(flex, ext):
            if flex < threshold and ext < threshold: # doble activacion muscular
                self.setAction(EmgAction.COCONTRACCION)
        
            elif flex < threshold and ext >= threshold:
                self.setAction(EmgAction.FLEXION)  # Solo flexion activa
 
            elif ext < threshold and flex >= threshold:
                self.setAction(EmgAction.EXTENSION)  # Solo extension activa
        
            else:
                self.setAction(EmgAction.REPOSO)  # Ambas inactivas, reposo
            
            return True
		
        return False  

"""
Uso
 -> inicializar objeto tipo Emg con los topics a leer y despues leer en un while True
   emgObj = Emg("/emg/flex", "/emg/ext")
   while True:
       emgObj.assign_action()
       accion = emgObj.getAction()
       # if accion == EmgAction.COCONTRACCION then cambiar de articulacion

#Ejemplo sin conexion a MQTT
# objeto tipo emg
emgObj =  Emg("/emg/flexion","/emg/extension")
isOk = True
while isOk:
# simular data adquirida
#emgObj.setFlex(1.2) # flexion detectada 
#emgObj.setExt(1.1) # extension detectada
    isOk = emgObj.assign_action() # prueba sin conexion a mqtt de la logica de acciones
    print(emgObj.getAction())
"""
