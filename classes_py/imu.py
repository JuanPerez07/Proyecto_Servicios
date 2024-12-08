"""
Clase IMU
	Atributos:
        - action_j4 y action_j5 (tipo enum de las acciones posibles)
        - j4 y j5 ( lo que se recibe del topico mqqtt) 
        - cadenas string de los topics como variables de clase
	Metodos:
        - getActions (devuelve las acciones posibles)
        - getStatus(devuelve la accion leida de los topics del sensor)

"""
#from subscriber import Subscriber # class import
from classes_py.subscriber import Subscriber
from enum import Enum # enum type
# class Action -> encode actions based on IMUsignals
class Imu_action(Enum):
    REPOSO = 0
    HORARIO = 1
    ANTIHORARIO = 2
    
# class IMU
class IMU:
    # Constructor based on topic names and umbral default a 2 Voltios
    def __init__(self, j4_topic, j5_topic, umbral=2.0):
        # instance variables
        self.umbral = float(umbral) # umbral ON/OFF
        self.action_j4 = Imu_action.REPOSO
        self.action_j5 = Imu_action.REPOSO
        self.j4 = 0
        self.j5 = 0 
        
        # class variables
        IMU.J4_TOPIC = j4_topic
        IMU.J5_TOPIC = j5_topic
    """
    SETTERS
    """
    def setJ4Action(self, action):
        self.action_j4 = action

    def setJ5Action(self, action):
        self.action_j5 = action
    
    def setJ4(self, joint_mov):
        self.j4 = int(joint_mov)

    def setJ5(self, joint_mov):
        self.action_j5 = int(joint_mov)
    
    """
    GETTERS    
    """
    def getJ4(self):
        return self.j4

    def getJ5(self):
        return self.j5
    
    def getJ4Action(self):
        return self.action_j4
    
    def getJ5Action(self):
        return self.action_j5
    
    """
    CLASS METHOD
    """
    @classmethod
    def read_is_valid(cls, j4_value, j5_value): 
        return j4_value is not None and j4_value >= 0 and j4_value <=2 and j5_value is not None and j5_value >= 0 and j5 <= 2

    """
    INSTANCE METHODS
    """
    # set the j4 and j4 values read from topic /imu
    def read_mqtt(self):
        # instance Subscriber objects to read topics /imu/j4 and /imu/j5
        sub_j4 = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt)
        sub_j5 = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt)
        
        # set the topic names
        sub_j4.setTopic(IMU.J4_TOPIC)
        sub_j5.setTopic(IMU.J4_TOPIC)

        # save values read from the broker
        self.setJ4(sub_j4.getMsg())
        self.setJ5(sub_j5.getMsg())        

    def assign_action(self, read_broker=True): # bool parameter to read broker, by default True
        # read from the mqtt
        if read_broker:
            self.read_mqtt()
        # get the instance's j4 and j5 values
        j4 = self.getJ4()
        j5 = self.getJ5()

        # classify action if read is valid
        if IMU.read_is_valid(j4, j5):
            if j4 == 0: # resposo del joint
                self.setJ4Action(Imu_action.REPOSO)
            elif j4 == 1:
                self.setJ4Action(Imu_action.HORARIO)  # giro horario del joint
 
            elif j4 == 2:
                self.setJ4Action(Imu_action.ANTIHORARIO)  # giro antihorario del joint

            if j5 == 0: # reposo del joint
                self.setJ5Action(Imu_action.REPOSO)
            elif j5 == 1:
                self.setJ5Action(Imu_action.HORARIO)  # giro horario del joint
 
            elif j5 == 2:
                self.setJ5Action(Imu_action.ANTIHORARIO)  # giro antihorario del joint
            
            return True
		
        return False  

