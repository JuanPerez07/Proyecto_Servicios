# Importar las bibliotecas necesarias
import pandas as pd
import matplotlib.pyplot as plt
ADC_MAX_VALUE = 4095

FIG_NAME = 'simulation_2_channels'
FILE = './csv/2_channel.csv'

# Leer el archivo CSV
try:
    df = pd.read_csv(FILE)

    # Verificar las primeras filas para asegurarse de que los datos se cargaron correctamente
    #print(df.head())

    # Crear un gráfico de los dos canales de señal EMG a lo largo del tiempo
    plt.figure(figsize=(10, 6))

    # Graficar el canal flex_value
    plt.plot(df['tiempo'], df['flex_value'], label='Canal Flex', color='b')

    # Graficar el canal ext_value
    plt.plot(df['tiempo'], df['ext_value'], label='Canal Ext', color='r')

    # Agregar etiquetas y título
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Voltaje (V)')
    plt.title('Señales EMG de los Canales Flex y Ext')
    plt.legend()

    # Mostrar el gráfico
    plt.grid(True)
    str = FIG_NAME + '.png'
    plt.savefig(str)
    #plt.show()

except FileNotFoundError:
    print(f"Error: El archivo '{file_path}' no se encuentra en el directorio especificado.")
except pd.errors.EmptyDataError:
    print(f"Error: El archivo '{file_path}' está vacío.")
except Exception as e:
    print(f"Ocurrió un error al leer el archivo: {e}")

"""
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
#plt.show()
str = FIG_NAME + '.png'
plt.savefig(str)
"""

