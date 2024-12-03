import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
import threading
import time
import random

# Configuración de simulación
SIMULATION_MODE = True  # Cambiar a False si se quiere usar MQTT
TOPIC_AXIS_4 = "/imu/j1"
TOPIC_AXIS_5 = "/imu/j2"

# Clase principal de la aplicación
class RobotInterface:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Robot ABB IRB 120")

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

        # Crear LEDs grandes encima de las articulaciones
        led_radius = 20  # Radio del LED

        # LED para la articulación 4
        self.led_axis_4 = self.canvas.create_oval(
            500 - led_radius, 200 - led_radius,
            500 + led_radius, 200 + led_radius,
            fill="gray", outline="black"
        )

        # LED para la articulación 5
        self.led_axis_5 = self.canvas.create_oval(
            580 - led_radius, 250 - led_radius,
            580 + led_radius, 250 + led_radius,
            fill="gray", outline="black"
        )

        # Iniciar hilo para simulación o MQTT
        if SIMULATION_MODE:
            self.simulation_thread = threading.Thread(target=self.simulate_movement, daemon=True)
        else:
            self.mqtt_thread = threading.Thread(target=self.update_leds, daemon=True)

        if SIMULATION_MODE:
            self.simulation_thread.start()
        else:
            self.mqtt_thread.start()

    def update_leds(self):
        from suscriber import Subscriber, server_mqtt, puerto_mqtt  # Importación local para usar MQTT
        # Configurar suscriptores MQTT para ambos ejes
        sub_4 = Subscriber(server_mqtt, puerto_mqtt)
        sub_4.setTopic(TOPIC_AXIS_4)

        sub_5 = Subscriber(server_mqtt, puerto_mqtt)
        sub_5.setTopic(TOPIC_AXIS_5)

        while True:
            # Obtener mensajes MQTT
            msg_4 = sub_4.getMsg()
            msg_5 = sub_5.getMsg()

            print(f"Mensaje eje 4: {msg_4}, Mensaje eje 5: {msg_5}")

            # Actualizar LEDs según el estado de los ejes
            self.set_leds(msg_4, msg_5)

    def simulate_movement(self):
        """Simula los mensajes de los ejes 4 y 5."""
        while True:
            # Simulación de mensajes para ejes 4 y 5
            msg_4 = random.choice(["1", "2", "0"])  # 1: derecha, 2: izquierda, 0: sin movimiento
            msg_5 = random.choice(["1", "2", "0"])
            print(f"[Simulación] Mensaje eje 4: {msg_4}, Mensaje eje 5: {msg_5}")

            # Actualizar LEDs según los mensajes simulados
            self.set_leds(msg_4, msg_5)

            time.sleep(1)  # Espera de 1 segundo entre simulaciones

    def set_leds(self, msg_4, msg_5):
        """Actualiza el estado de los LEDs en función de los mensajes recibidos."""
        # Resetear LEDs a color "apagado" (gris)
        self.canvas.itemconfig(self.led_axis_4, fill="gray")
        self.canvas.itemconfig(self.led_axis_5, fill="gray")

        # Actualizar LED del eje 4
        if msg_4 == "1":
            self.canvas.itemconfig(self.led_axis_4, fill="green")  # Girando derecha
        elif msg_4 == "2":
            self.canvas.itemconfig(self.led_axis_4, fill="red")  # Girando izquierda

        # Actualizar LED del eje 5
        if msg_5 == "1":
            self.canvas.itemconfig(self.led_axis_5, fill="green")  # Girando derecha
        elif msg_5 == "2":
            self.canvas.itemconfig(self.led_axis_5, fill="red")  # Girando izquierda


# Crear ventana de la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotInterface(root, "abb_irb120.png")
    root.mainloop()

