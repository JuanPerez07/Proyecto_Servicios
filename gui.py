"""
class GUI -> global interface for user info
"""
import tkinter as tk
import threading
import time
import random
import os
import numpy as np
from tkinter import Canvas
from PIL import Image, ImageTk

from classes_py.emg import *
from classes_py.imu import *

SIMULATION_MODE = True # if we use mqtt protocol -> False
LED_RADIUS = 20 # radius of the joint id 
OFF = "gray" # color of the joint id to symbolize it is not active
DATA_DIR = os.path.join(os.getcwd(), "images") # dir of the images used by the gui
ABB_IMG_PATH = os.path.join(DATA_DIR, 'abb_irb120.png') # img_path

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
        self.canvas = Canvas(root, width=self.img_width, height=self.img_height)
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

        # start thread 
        self.simulation_thread = threading.Thread(target=self.simulate_movement, daemon=True)
        self.simulation_thread.start()
        
            

    def create_leds(self, led_radius):
        # create each led_axis for each joint
        for i in range(self.num_leds):
            self.led_axis[i] = self.canvas.create_oval(
                self.led_pos[i][0] - led_radius, self.led_pos[i][1] - led_radius,
                self.led_pos[i][0] + led_radius, self.led_pos[i][1] + led_radius,
                fill=OFF, outline="black"
            )

    def set_leds(self, i):
        # sets the led i according to its value
        self.canvas.itemconfig(self.led_axis[i], fill=self.led_value[i])

    def update_leds(self, id, joint): # given the i-joint we control and an id for the sensor responsible
        action = None
        if id == 'emg': # emg control
            action = self.emg.getAction()
        elif id == 'inertial':
            action = []
            action.append(self.imu.getJ4Action())
            action.append(self.imu.getJ5Action())
        else:
            print("Cannot update leds, wrong id given. ID must be {'emg'} or {'inertial'}")
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
                if action[0] == Imu_action.REPOSO:
                    value[0] = OFF

                elif action[0] == Imu_action.ANTIHORARIO: # giro positivo
                    value[0] = "green"

                elif action[0] == Imu_action.HORARIO: # giro negativo: clockwise
                    value[0] = "red"

                else:
                    value = None

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
                for i in range(self.num_leds - 1):
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
            for j in range(2): # j = [0, 1]
                self.led_value[joint + j] = value_imu[j]
                self.set_leds(joint + j)
        
    
    def simulate_movement(self):
        """Simula los mensajes de los 3 primeros DOFs del ABB"""
        isOk = True
        joint = 0
        while True:
            if SIMULATION_MODE: # sin conexion a sensores mediante MQTT
                flex = random.choice([2.5, 1.75])
                ext = random.choice([2.5, 1.75])

                self.emg.setFlex(flex)
                self.emg.setExt(ext)
            
                isOk = self.emg.assign_action(False)
                action = self.emg.getAction()
                print(f"Controlling joint {joint}, detected: {action}")
                if action == EmgAction.COCONTRACCION:
                    joint += 1
                    if joint == 3:
                        joint = 0
                # Actualizar LEDs segun los mensajes simulados
                self.update_leds('emg', joint)

                time.sleep(1)  # Espera de 1 segundo entre simulaciones

            else:

                isOk = self.emg.assign_action() # asignar accion segun sensores de mqtt
                action = self.emg.getAction()
                if action == EmgAction.COCONTRACCION:
                    joint += 1
                # actualizar LEDs
                self.update_leds('emg', joint)

# Crear ventana de la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    # number of joints
    num_joints = 5
    # create emgObj and assign values
    emgObj = Emg("/emg", "/elef")
    imuObj = IMU("/j4", "/j5")
    # create interface, params = root, image_path, number_joints, emgObject=None, imuObject=None
    app = RobotInterface(root, ABB_IMG_PATH, num_joints, emgObj)
    root.mainloop()