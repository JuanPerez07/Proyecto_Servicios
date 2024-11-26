import tkinter as tk
from tkinter import Canvas
from PIL import Image
from PIL import ImageTk
import threading
from suscriber import Subscriber
from suscriber import server_mqtt 
from suscriber import puerto_mqtt

# Configuración de topics MQTT
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

        # Crear un lienzo para la interfaz
        self.canvas = Canvas(root, width=self.img.width, height=self.img.height)
        self.canvas.pack()

        # Mostrar imagen en el lienzo
        self.canvas.create_image(180, 0, anchor="nw", image=self.tk_img)

        # Crear flechas para los ejes 4 y 5
        self.arrow_4 = self.canvas.create_polygon(300, 100, 320, 120, 300, 140, fill="gray", outline="black")  # Eje 4
        self.arrow_5 = self.canvas.create_polygon(400, 200, 420, 220, 400, 240, fill="gray", outline="black")  # Eje 5

        # Iniciar la conexión MQTT en un hilo separado
        self.mqtt_thread = threading.Thread(target=self.update_arrows, daemon=True)
        self.mqtt_thread.start()

    def update_arrows(self):
        print("He llegado a update_arrows")
        # Configurar suscriptores MQTT para ambos ejes
        sub_4 = Subscriber(server_mqtt, puerto_mqtt)
        sub_4.setTopic(TOPIC_AXIS_4)

        sub_5 = Subscriber(server_mqtt, puerto_mqtt)
        sub_5.setTopic(TOPIC_AXIS_5)

        while True:
            # Obtener mensajes MQTT
            msg_4 = sub_4.getMsg()
            msg_5 = sub_5.getMsg()

            print(f"Mensaje 4: {msg_4}")
            # Actualizar color de las flechas según el valor recibido
            if msg_4 == "1":
                self.canvas.itemconfig(self.arrow_4, fill="green")  # Girando en dirección positiva
            elif msg_4 == "2":
                self.canvas.itemconfig(self.arrow_4, fill="red")  # Girando en dirección negativa
            else:
                self.canvas.itemconfig(self.arrow_4, fill="gray")  # Sin movimiento

            if msg_5 == "1":
                self.canvas.itemconfig(self.arrow_5, fill="green")
            elif msg_5 == "2":
                self.canvas.itemconfig(self.arrow_5, fill="red")
            else:
                self.canvas.itemconfig(self.arrow_5, fill="gray")

# Crear ventana de la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotInterface(root, "abb_irb120.png")
    root.mainloop()
