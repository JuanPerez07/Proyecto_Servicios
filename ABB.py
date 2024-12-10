#! /usr/bin/env python
# ROS Distro: Kinetic

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from math import pi
from std_msgs.msg import String
from moveit_commander.conversions import pose_to_list
from tf.transformations import euler_from_quaternion, quaternion_from_euler
# import classes 
from classes_py.emg import *
from classes_py.imu import *
from gui import RobotInterface 

# frecuencia lectura sensores del ABB
FREQ =  2 # Hz

def all_close(goal, actual, tolerance):
    
    all_equal = True
    if type(goal) is list:
        for index in range(len(goal)):
            if abs(actual[index] - goal[index]) > tolerance:
                return False

    elif type(goal) is geometry_msgs.msg.PoseStamped:
        return all_close(goal.pose, actual.pose, tolerance)

    elif type(goal) is geometry_msgs.msg.Pose:
        return all_close(pose_to_list(goal), pose_to_list(actual), tolerance)

    return True


class ABB_IRB120(object):

    def __init__(self):
        super(ABB_IRB120, self).__init__()

    ## Inicializamos moveit_commander y el nodo rospy:
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('moving_irb120_robot', anonymous=True)
        
        ## Creamos el objeto 'RobotCommander':
        robot = moveit_commander.RobotCommander()

        ## Creamos el objeto 'PlanningSceneInterface':
        scene = moveit_commander.PlanningSceneInterface()

        ## Instanciamos uno o varios objetos 'MoveGroupCommander', los
        ## cuales son interfaces para un grupo de planificacion (grupo
        ## de articulaciones).
        ## Esta interfaz puede utilizarse para planificar y ejecutar
        ## movimientos:
        arm_group = moveit_commander.MoveGroupCommander("manipulator")

        ## Creamos el DisplayTrajectory ROS publisher para visualizar trayectorias en RViz:
        display_trajectory_publisher = rospy.Publisher('/arm_group/display_planned_path', moveit_msgs.msg.DisplayTrajectory, queue_size=20)

        ## Recopilar informacion basica
        ## ^^^^^^^^^^^^^^^^^^^^^^^^^
        # Nombre del marco de referencia para este robot:
        planning_frame = arm_group.get_planning_frame()

        # Nombre del eslabon del efector final para este grupo:
        eef_link = arm_group.get_end_effector_link()

        # Lista con los grupos del robot:
        group_names = robot.get_group_names()
        # Variables
        self.robot = robot #Robot
        self.scene = scene #Escena
        self.arm_group = arm_group #Grupo del brazo robotico
        self.display_trajectory_publisher = display_trajectory_publisher
        self.planning_frame = planning_frame
        self.eef_link = eef_link #Link del efector final
        self.group_names = group_names #Grupos del robot
        self.freq = FREQ

    # Forward Kinematics (FK): Para mover el brazo robotico segun los
    # valores de las articulaciones
    def move_joint_arm(self, joint_goal):
        arm_group = self.arm_group
        # Al comando go se le pasan los nuevos valores para cada
        # articulacion
        arm_group.go(joint_goal, wait=True)
        # Para garantizar la ausencia de movimientos residuales
        arm_group.stop()
        # Comprobamos los nuevos valores de las articulaciones:
        current_joints = arm_group.get_current_joint_values()
        return all_close(joint_goal, current_joints, 0.01)

    # Para mover el robot a una posicion previamente establecida
    # En nuestro caso, podemos utilizar "home" o "all-zeros"
    def go_to_target(self, target="home", group_name = "manipulator"):
        arm_group = moveit_commander.MoveGroupCommander(group_name)
        arm_group.set_named_target(target)
        plan = arm_group.go(wait=True)
        arm_group.stop()
        clear_joint_value_targets()
        arm_group.clear_pose_targets()
        return 1

def speed_control(ABB, indice, sentido, velocidad=0.12):
    joint = ABB.arm_group.get_current_joint_values()
    joint[indice] = joint[indice] + velocidad*sentido
    
    ABB.move_joint_arm(joint)
    
    rospy.sleep(1/ABB.freq)

def move_home(ABB):
    joint = ABB.arm_group.get_current_joint_values()

    if all(pos == 0 for pos in joint):
        print("The arm is already in the HOME position. No movement needed.")
        return
    else:

        print ("Moving pose HOME")	
        joint[0] = 0
        joint[1] = 0
        joint[2] = 0
        joint[3] = 0
        joint[4] = 0
        joint[5] = 0
        ABB.move_joint_arm(joint)

        return
def button_connection():
    sub_bt = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt)
    sub_bt.setTopic("/button")
    return int(sub_bt.getMsg())
    
    
# Funcion principal
def main():
    print ("Setting up the moveit_commander")
    ABB = ABB_IRB120()
    
    print ("Press Enter to execute")
    raw_input()
    move_home(ABB)
    estado = 0
    indice = 0
    isOk = True
    sentido = 0
    multi_joint = False
    indiceJ4 = 3
    indiceJ5 = 4
    sentidoJ4 = 0
    sentidoJ5 = 0
    while not rospy.is_shutdown():
        try:
            print("Conectandose al MQTT")
            while isOk or not rospy.is_shutdown():
                emgObj = Emg("/emg/flexion", "/emg/extension")
                imuObj = IMU("/imu/j4", "/imu/j5")

                isOk = emgObj.assign_action() and imuObj.assign_action() # false pq no hay mqtt conectado
                
                # accion detectada
                emg_accion = emgObj.getAction()
                imu_j4action = imuObj.getJ4Action()
                imu_j5action = imuObj.getJ5Action()
                button_state = button_connection()
                
                if estado == 0: #estado inicial de la máquina de estados
                    multi_joint = False
                    indice = 0
                    sentido = 0
                    if emg_accion == EmgAction.COCONTRACCION:
                    
                        print("CONTROLANDO JOINT 1")
                        estado = 1
                        indice = 0
                        sentido = 0
                elif estado == 1: # controlar el joint 1
                    sentido = 0
                    indice = 0 
                    if emg_accion == EmgAction.COCONTRACCION:
                        print("CONTROLANDO JOINT 2")
                        indice = 1
                        estado = 2
                        sentido = 0
                    elif emg_accion == EmgAction.FLEXION:
                        sentido = 1
                    elif emg_accion == EmgAction.EXTENSION:
                        sentido = -1
                    elif button_state == 1:
                        estado = 0
                        sentido = 0
                        indice = 0
                elif estado == 2: #controlar el joint 2
                    sentido = 0
                    indice = 1
                    if emg_accion == EmgAction.COCONTRACCION:
                        print("CONTROLANDO JOINT 3")
                        indice = 2
                        estado = 3
                    elif emg_accion == EmgAction.FLEXION:
                        sentido = 1
                    elif emg_accion == EmgAction.EXTENSION:
                        sentido = -1
                    elif button_state == 1:
                        estado = 0
                        sentido = 0
                        indice = 0
                elif estado == 3: # controlar el joint 3
                    sentido = 0
                    indice = 2
                    if emg_accion == EmgAction.COCONTRACCION:
                        print("CONTROLANDO JOINTS 4 Y 5")
                        estado = 4
                        sentido = 0
                        indice = 0
                        
                    elif emg_accion == EmgAction.FLEXION:
                        sentido = 1
                    elif emg_accion == EmgAction.EXTENSION:
                        sentido = -1
                    
                    elif button_state == 1:
                        estado = 0
                        sentido = 0
                        indice = 0
                elif estado == 4:
                    multi_joint = True
                    # control del joint 4
                    if imu_j4action == Imu_action.REPOSO:
                        sentidoJ4 = 0
                    elif imu_j4action == Imu_action.HORARIO:
                        sentidoJ4 = 1
                    elif imu_j4action == Imu_action.ANTIHORARIO:
                        sentidoJ4 = -1
                    # control del joint 5
                    if imu_j5action == Imu_action.REPOSO:
                        sentidoJ5 = 0
                    elif imu_j5action == Imu_action.HORARIO:
                        sentidoJ5 = 1
                    elif imu_j5action == Imu_action.ANTIHORARIO:
                        sentidoJ5 = -1
                    elif button_state == 1:
                        estado = 0
                        sentido = 0
                        indice = 0
                        sentidoJ4 = 0
                        sentidoJ5 = 0
                                                
                #enviar al robot que mueva en un sentido la articulacion i
                if multi_joint and estado != 0:
                    speed_control(ABB, indice, sentido)
                elif estado == 4 and nulti_joint:
                    speed_control(ABB, indiceJ4, sentidoJ4)
                    speed_control(ABB, indiceJ5, sentidoJ5)
            move_home(ABB)
        except rospy.ROSInterruptException:
            move_home(ABB)
            return
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    main()

