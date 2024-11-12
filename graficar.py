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

    # Resaltar valores concretos con triangulos negros
    plt.scatter(df['tiempo'], df['flex_value'], color='black', marker='v', label='Flex values', zorder=5)
    plt.scatter(df['tiempo'], df['ext_value'], color='brown', marker='v', label='Extension values', zorder=5)

    # Agregar etiquetas y título
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Voltaje (V)')
    plt.title('Señales EMG de los Canales Flex y Ext')
    
    # Mostrar leyenda en la esquina inferior derecha, con tamaño reducido y cuadro pequeño
    plt.legend(loc='lower left', fontsize=6, frameon=True, borderpad=1, borderaxespad=0.5)

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


