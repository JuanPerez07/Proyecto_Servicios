# Importar las bibliotecas necesarias
import pandas as pd
import matplotlib.pyplot as plt
ADC_MAX_VALUE = 4095

FIG_NAME = 'plot_ext'
FILE = 'data_ext.csv'

def scaleVoltage(data, voltage=3.3):
    data["Valor"] = (data["Valor"]/ADC_MAX_VALUE) * voltage
    return data

def correctTime(data):
    data["Tiempo"] = range(1, len(data)+ 1)
    return data
# Ruta del archivo CSV
file_path = FILE

# Leer el archivo CSV, saltando las filas problemáticas
data = pd.read_csv(file_path, header=None, names=["Tiempo", "Valor"], on_bad_lines='skip')

# Filtrar solo las filas donde "Tiempo" y "Valor" sean numéricos
data = data[pd.to_numeric(data["Tiempo"], errors='coerce').notna()]
data = data[pd.to_numeric(data["Valor"], errors='coerce').notna()]

# Convertir la columna "Tiempo" a enteros y "Valor" a flotantes
data["Tiempo"] = data["Tiempo"].astype(int)
data["Valor"] = data["Valor"].astype(float)
# corregir indices del tiempo y escalar el voltaje
data = correctTime(data)
data = scaleVoltage(data)
# Graficar los datos interpolados
plt.figure(figsize=(10, 5))
plt.plot(data.index, data["Valor"], label="Voltaje", color="b")

# Destacar los puntos capturados originalmente con triángulos rojos
original_points = data[pd.to_numeric(data["Tiempo"], errors='coerce').notna()]
original_points = data[pd.to_numeric(data["Valor"], errors='coerce').notna()]
original_points["Tiempo"] = original_points["Tiempo"].astype(int)
original_points["Valor"] = original_points["Valor"].astype(float)

# Graficar los puntos originales
plt.plot(original_points["Tiempo"], original_points["Valor"], 'r^', label="Datos Capturados")

# Etiquetas y título de la gráfica
plt.xlabel("Tiempo")
plt.ylabel("Voltaje")
plt.title("Señal EMG de la flexión de bíceps")
plt.legend()
plt.grid(True)
#plt.show()
str = FIG_NAME + '.png'
plt.savefig(str)
