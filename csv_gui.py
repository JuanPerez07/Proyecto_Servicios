"""
interfaz de la parte de EMG
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import time
import threading
from PIL import Image, ImageTk  # Asegúrate de instalar Pillow: pip install pillow

# Variables globales
current_joint = "JOINT 1"
joints = ["JOINT 1", "JOINT 2", "JOINT 3"]
booleano = False

def cargar_archivo():
    """Carga un archivo CSV y comienza a procesar los datos."""
    archivo = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    if archivo:
        try:
            # Leer el CSV
            data = pd.read_csv(archivo)

            # Validar si el archivo tiene las columnas esperadas
            columnas_requeridas = ["tiempo", "flex_value", "ext_value"]
            if not all(col in data.columns for col in columnas_requeridas):
                messagebox.showerror(
                    "Error",
                    f"El archivo debe contener las columnas: {', '.join(columnas_requeridas)}",
                )
                return
            
            # Lanzar procesamiento en un hilo separado
            threading.Thread(target=procesar_datos, args=(data,)).start()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el archivo: {e}")

def procesar_datos(data):
    """Procesa los datos del CSV línea por línea con un retardo."""
    global current_joint
    global booleano
    boton_cargar.config(state=tk.DISABLED)  # Deshabilitar botón mientras se procesan datos
    for index, row in data.iterrows():
        # Mostrar las columnas con diferentes colores
        texto_resultados.insert(tk.END, f"Fila {index + 1}:\n", "fila")
        texto_resultados.insert(
            tk.END, f"  Tiempo (s): {row['tiempo']}\n", "tiempo")
        texto_resultados.insert(
            tk.END, f"  Flexión (V): {row['flex_value']}\n", "flex_value")
        texto_resultados.insert(
            tk.END, f"  Extensión (V): {row['ext_value']}\n", "ext_value")
        texto_resultados.insert(tk.END, "-"*40 + "\n", "separator")

        # Determinar el estado y actualizar el cuadro de estado
        estado = determinar_estado(row["flex_value"], row["ext_value"])
        cuadro_estado.delete("1.0", tk.END)
        cuadro_estado.insert(tk.END, estado)

        # Cambiar el joint si es "CO-CONTRACCIÓN"
        if estado == "CO-CONTRACCIÓN" and booleano == False:
            current_joint = joints[(joints.index(current_joint) + 1) % len(joints)]
            cuadro_joint.delete("1.0", tk.END)
            cuadro_joint.insert(tk.END, current_joint)
            booleano = True
        elif estado != "CO-CONTRACCIÓN":
            booleano = False

        texto_resultados.see(tk.END)  # Hacer scroll automáticamente
        time.sleep(1)  # Retardo de 1 segundo
    actualizar_estado("Procesamiento completo.")
    boton_cargar.config(state=tk.NORMAL)  # Habilitar botón al terminar

def determinar_estado(flex_value, ext_value):
    """Determina el estado del robot basado en los valores."""
    if flex_value > 2.0 and ext_value > 2.0:
        return "REPOSO"
    elif flex_value < 2.0 and ext_value > 2.0:
        return "FLEXIÓN"
    elif flex_value > 2.0 and ext_value < 2.0:
        return "EXTENSIÓN"
    elif flex_value < 2.0 and ext_value < 2.0:
        return "CO-CONTRACCIÓN"
    return "DESCONOCIDO"

def actualizar_estado(mensaje):
    """Actualiza el estado en la interfaz."""
    etiqueta_estado.config(text=mensaje)

# Crear la ventana principal
root = tk.Tk()
root.title("Lector de CSV con Colores")

root.geometry("1280x720")  # Establecer tamaño fijo
root.resizable(False, False)  # Deshabilitar redimensionado

# Crear un frame para los controles
frame_controles = tk.Frame(root)
frame_controles.pack(pady=10, padx=10)

boton_cargar = tk.Button(frame_controles, text="Cargar Archivo CSV", command=cargar_archivo)
boton_cargar.grid(row=0, column=0, padx=5, pady=5)

etiqueta_estado = tk.Label(frame_controles, text="Estado: Esperando archivo...")
etiqueta_estado.grid(row=0, column=1, padx=5, pady=5)

# Crear un contenedor horizontal para el cuadro de texto y la imagen
frame_contenido = tk.Frame(root)
frame_contenido.pack(fill=tk.BOTH, expand=True)

# Posicionar el cuadro de texto a la izquierda
texto_resultados = tk.Text(frame_contenido, height=30, width=50)
texto_resultados.pack(side="left", padx=10, pady=10)

# Crear cuadros de texto para estado y joint
frame_estado = tk.Frame(frame_contenido)
frame_estado.pack(side="left", padx=20)

cuadro_estado = tk.Text(frame_estado, height=5, width=27, bg="lightyellow", font=("Helvetica", 24))
cuadro_estado.pack(pady=10)

cuadro_joint = tk.Text(frame_estado, height=5, width=27, bg="lightblue", font=("Helvetica", 24))
cuadro_joint.pack(pady=10)

# Cargar y redimensionar la imagen
imagen_original = Image.open("assets/abb_irb120.png")  # Cambia por la ruta correcta
imagen_resized = imagen_original.resize((400, 400))
imagen_tk = ImageTk.PhotoImage(imagen_resized)

# Posicionar la imagen a la derecha
label_imagen = tk.Label(frame_contenido, image=imagen_tk)
label_imagen.image = imagen_tk  # Evitar que el recolector de basura elimine la referencia
label_imagen.pack(side="right", padx=10, pady=10)

# Configuración de estilos de colores
texto_resultados.tag_configure("tiempo", foreground="blue", font=("Helvetica", 12, "bold"))
texto_resultados.tag_configure("flex_value", foreground="green", font=("Helvetica", 12))
texto_resultados.tag_configure("ext_value", foreground="red", font=("Helvetica", 12))
texto_resultados.tag_configure("separator", foreground="gray", font=("Helvetica", 10, "italic"))
texto_resultados.tag_configure("fila", foreground="black", font=("Helvetica", 14, "bold"))

# Inicializar cuadros de texto
cuadro_estado.insert(tk.END, "REPOSO")
cuadro_joint.insert(tk.END, "JOINT 1")

# Ejecutar la aplicación
root.mainloop()

