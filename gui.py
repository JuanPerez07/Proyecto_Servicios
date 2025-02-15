#!/usr/bin/python
"""
class GUI -> global interface for user info
"""
import Tkinter as tk
import threading
import time
import random
import os
import numpy as np
from Tkinter import Canvas
from PIL import Image, ImageTk

from classes_py.emg import *
from classes_py.imu import *

SIMULATION_MODE = True # if we use mqtt protocol must be false
LED_RADIUS = 20 # radius of the joint id 
OFF = "gray" # color of the joint id to symbolize it is not active
DATA_DIR = os.path.join(os.getcwd(), "images") # dir of the images used by the gui
ABB_IMG_PATH = os.path.join(DATA_DIR, 'abb_irb120.png') # img_path
LED_IMG_PATH = os.path.join(DATA_DIR, 'led_colour_code.png') # img_path
FREQ = 4 # hz

def button_connection():
    sub_bt = Subscriber(Subscriber.server_mqtt, Subscriber.puerto_mqtt)
    sub_bt.setTopic("/button")
    return int(sub_bt.getMsg())

class RobotInterface:
    def __init__(self, root, image_path, num_leds=5, emgObj=None, inertialObj=None):
        # object Tkinter with title
        self.root = root
        self.root.title("Robot ABB IRB 120")

        # instances for emgObj and inertialObj
        self.emg = emgObj
        self.imu = inertialObj

        # Cargar imagen del robot
        self.img = Image.open(image_path)
        self.tk_img = ImageTk.PhotoImage(self.img)

        # Dimensiones de la imagen
        self.img_width = self.img.width
        self.img_height = self.img.height

        # Crear un lienzo para la interfaz
        self.canvas = Canvas(root, width=self.img_width + 500, height=self.img_height)
        self.canvas.pack()
        
        # Mostrar imagen en el lienzo
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        
        # set the number of leds and their position
        self.num_leds = num_leds # numer of leds involved
        self.led_axis = np.full(self.num_leds, None) # numpy array of leds type 
        self.led_pos = np.asarray([[300,600], [265, 460], [275, 255], [500, 200], [580, 250]]) # image pixel positions
        
        # create leds for each joint
        self.create_leds(LED_RADIUS)

        # create the possible values for each led
        self.led_value = []
        for i in range (self.num_leds):
            self.led_value.append(OFF)
        
        self.create_boxes() #Create the boxes to the right of the image
        #TODO : modified
        self.canvas.create_text(self.img_width + 50, 55, text='Muscle Action', anchor='nw', font='Arial 32', fill='black')
        self.canvas.create_text(self.img_width + 50, 355, text='Joint', anchor='nw', font='Arial 32', fill='black')
        
        # start thread 
        self.simulation_thread = threading.Thread(target=self.simulate_movement)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
    def create_boxes(self):
        # Create the main box, where the other boxes will be inside it
        self.canvas.create_rectangle(self.img_width + 10, 10, self.img_width + 490, self.img_height - 10, fill='white', outline='black')
        j = 0 # It is used to change the position of the boxes in each iteration
        for i in range(4): # Create the boxes which contain information about the direction of joint rotation and the type of muscle movement
            x0 = self.img_width + 20 # Border 1
            y0 = 20 + j # Border 1
            x1 = self.img_width + 480 # Border 2
            y1 = 170 + j # Border 2
            if i % 2 == 0:
                self.canvas.create_rectangle(x0, y0, x1, y1, fill='light grey', outline='black') # Create the rectange using two borders
            else:
                self.canvas.create_rectangle(x0, y0, x1, y1, fill='white', outline='black') # Create the rectange using two borders
            j += 150 # To change the box size

    def create_leds(self, led_radius):
        # create each led_axis for each joint
        for i in range(self.num_leds): #[0,1,2,3,4]
            self.led_axis[i] = self.canvas.create_oval(
                self.led_pos[i][0] - led_radius, self.led_pos[i][1] - led_radius,
                self.led_pos[i][0] + led_radius, self.led_pos[i][1] + led_radius,
                fill=OFF, outline="black"
            )

    def set_leds(self, i):
        # sets the led i according to its value
        self.canvas.itemconfig(self.led_axis[i], fill=self.led_value[i])

    def update_leds(self, id, joint): # given the i-joint we control and an id for the sensor responsible
        action, action_list = None, None
        if id == 'emg': # emg control
            action = self.emg.getAction()
        elif id == 'imu':
            action_list = []
            action_list.append(self.imu.getJ4Action())
            action_list.append(self.imu.getJ5Action())
        else:
            print("Cannot update leds, wrong id given. ID must be 'emg' or 'inertial'")
        # classify action to swap color
        value_emg = None
        value_imu = [None, None]
        try:
            if joint < 3: # emg control
                if action == EmgAction.REPOSO:
                    value_emg = OFF

                elif action == EmgAction.FLEXION: # giro negativo
                    value_emg = "red"

                elif action == EmgAction.EXTENSION: # giro positivo 
                    value_emg = "green"

                else:
                    value_emg = None
                
            else: # inertial sens control
                # joint4 control
                if action_list[0] == Imu_action.REPOSO:
                    value_imu[0] = OFF

                elif action_list[0] == Imu_action.ANTIHORARIO: # giro positivo
                    value_imu[0] = "green"

                elif action_list[0] == Imu_action.HORARIO: # giro negativo: clockwise
                    value_imu[0] = "red"

                else:
                    value_imu[0] = None
                # joint5 control
                if action_list[1] == Imu_action.REPOSO:
                    value_imu[1] = OFF

                elif action_list[1] == Imu_action.ANTIHORARIO: # giro positivo
                    value_imu[1] = "green"

                elif action_list[1] == Imu_action.HORARIO: # giro negativo: clockwise
                    value_imu[1] = "red"

                else:
                    value_imu[1] = None

        except Exception as e:
            print("Error codificando value del led segun action", e)
            pass

        # set the leds according to their value
        if value_emg is not None and id == 'emg':
            if joint > 0: # set the previous joints OFF in case of skipping a joint 
                for i in range(joint + 1):
                    self.led_value[joint-i] = OFF
                    self.set_leds(joint-i)
            
            elif joint == 0: # set the rest of joints OFF, joints => {1,2,3,4}
                for i in range(self.num_leds - 1): # 4 iters -> [0,1,2,3]
                    self.led_value[i+1] = OFF
                    self.set_leds(i+1)
            # set the current joint we are controlling 
            self.led_value[joint] = value_emg
            self.set_leds(joint)

        if value_imu is not None and id == 'imu':
            # set OFF the previous joints
            for i in range(self.num_leds - 2):
                self.led_value[i] = OFF
                self.set_leds(i)
            # set the current joints -> last 2 dofs of the ABB
            j = 1 # joint = 3
            self.led_value[joint] = value_imu[j-1] # joint4
            self.set_leds(joint)
            self.led_value[joint+1] = value_imu[j] # joint5
            self.set_leds(joint+1)
                
        
    
    def simulate_movement(self):
        """Simula los mensajes de los 3 primeros DOFs del ABB"""
        isOk = True
        id_str = 'emg'
        joint = 0
        while True:
            if SIMULATION_MODE: # sin conexion a sensores mediante MQTT
                flex = random.choice([2.5, 1.75])
                ext = random.choice([2.5, 1.75])

                self.emg.setFlex(flex)
                self.emg.setExt(ext)
            
                isOk = self.emg.assign_action(False)
                action = self.emg.getAction()
                
                self.canvas.create_rectangle(self.img_width + 20, 170, self.img_width + 480, 320, fill='white') #Para que el texto de la accion no se superponga
                self.canvas.create_rectangle(self.img_width + 20, 470, self.img_width + 480, 620, fill='white') #Para que el texto del "joint" no se superponga
                
                if action == EmgAction.REPOSO:
                    self.canvas.create_text(self.img_width + 120, 225, text="REPOSO", anchor='nw', font='Arial 20', fill='black')    
                elif action == EmgAction.EXTENSION:
                    self.canvas.create_text(self.img_width + 100, 225, text="EXTENSION", anchor='nw', font='Arial 20', fill='green')
                elif action == EmgAction.FLEXION:
                    self.canvas.create_text(self.img_width + 120, 225, text="FLEXION", anchor='nw', font='Arial 20', fill='red')
                elif action == EmgAction.COCONTRACCION:
                    self.canvas.create_text(self.img_width + 30, 225, text="COCONTRACCION", anchor='nw', font='Arial 20', fill='black')
                else:
                    self.canvas.create_text(self.img_width + 30, 225, text="ERROR: NO DETECTED", anchor='nw', font='Arial 20', fill='black')
                
                
                
                self.canvas.create_text(self.img_width + 120, 525, text=str(joint+1), anchor='nw', font='Arial 20', fill='black')
                
                if action == EmgAction.COCONTRACCION:
                    joint += 1
                    if joint == 3:
                        joint = 0
                        id_str = 'imu'
                # Actualizar LEDs segun los mensajes simulados
                self.update_leds('emg', joint)

                time.sleep(1)  # Espera de 1 segundo entre simulaciones

            else:
                button_state = button_connection()
				# if pressed button returns to the starting state joint =0, id_str = 'emg'
                if button_state == 1:
                    id_str = 'emg'
                    joint = 0
                if button_state == 0 and self.emg.assign_action() and self.imu.assign_action():
                    action_imuJ4 = self.imu.getJ4Action()
                    action_imuJ5 = self.imu.getJ5Action()
                    action_emg = self.emg.getAction()
                    # actualizar leds
                    self.update_leds(id_str, joint)
                    # mostrar acciones de emg en la interfaz
                    self.canvas.create_rectangle(self.img_width + 20, 170, self.img_width + 480, 320, fill='white') #Para que el texto no se superponga
                    self.canvas.create_rectangle(self.img_width + 20, 470, self.img_width + 480, 620, fill='white') #Para que el texto del "joint" no se superponga
                
                    if action_emg == EmgAction.REPOSO:
                        self.canvas.create_text(self.img_width + 120, 225, text="REPOSO", anchor='nw', font='Arial 20', fill='black')    
                    elif action_emg == EmgAction.EXTENSION:
                        self.canvas.create_text(self.img_width + 100, 225, text="EXTENSION", anchor='nw', font='Arial 20', fill='green')
                    elif action_emg == EmgAction.FLEXION:
                        self.canvas.create_text(self.img_width + 120, 225, text="FLEXION", anchor='nw', font='Arial 20', fill='red')
                    elif action_emg == EmgAction.COCONTRACCION:
                        self.canvas.create_text(self.img_width + 30, 225, text="COCONTRACCION", anchor='nw', font='Arial 20', fill='black')
                    else:
                        self.canvas.create_text(self.img_width + 30, 225, text="ERROR: NO DETECTED", anchor='nw', font='Arial 20', fill='black')
                    # joint swap 
                    
                    self.canvas.create_text(self.img_width + 120, 525, text=str(joint+1), anchor='nw', font='Arial 20', fill='black')
                    
                    if action_emg == EmgAction.COCONTRACCION:
                        joint += 1
                        if joint == 4:
                            joint = 0
                            id_str = 'emg' 
                    # if we are in joint 3 -> id_str changes to 'imu'
                    if joint == 3:
                        id_str = 'imu'						
                
                time.sleep(1/FREQ)

# Crear ventana de la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    # number of joints
    num_joints = 5
    # create emgObj and assign values
    emgObj = Emg("/emg/flexion", "/emg/extension")
    imuObj = IMU("/imu/j4", "/imu/j5")
    # create interface, params = root, image_path, number_joints, emgObject=None, imuObject=None
    app = RobotInterface(root, ABB_IMG_PATH, num_joints, emgObj, imuObj)
    root.mainloop()
