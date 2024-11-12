import pandas as pd

# funcion para corregir time stamp
def correctTime(data):
    data["tiempo"] = range(1, len(data)+ 1)
    return data
# funcion para escalar el voltaje de los valores analogicos del .csv
def scaleVoltage(name,data, voltage=3.3):
    data["valor"] = (data["valor"]/ADC_MAX_VALUE) * voltage
    return data
# Cargar los datos de los archivos originales y adelantados
data_flex = pd.read_csv('./csv/data_flex.csv')
data_ext = pd.read_csv('./csv/data_ext.csv')

print(data_flex.columns)
# Renombrar columnas para identificarlas en el archivo combinado
data_flex.columns = ['tiempo', 'flex_value']
data_ext.columns = ['tiempo', 'ext_value']

# Corregir los instantes de tiempo
data_flex = correctTime(data_flex)
data_ext = correctTime(data_ext)

# Escalar a 3.3V
data_flex = scaleVoltage('flex_value', data_flex)
data_ext = scaleVoltage('ext_value', data_ext)

# Combinar los DataFrames en uno solo usando la columna 'tiempo'
combined_data = pd.merge(data_flex, data_ext, on='tiempo', how='outer')

# Seleccionar los datos del tiempo 20 al 40 del archivo original para añadir como filas adicionales
# Considerando que el índice comienza en 0, el intervalo (20-40) corresponde a filas 19 a 39
extra_rows = combined_data.iloc[19:40].copy()
extra_rows['tiempo'] += combined_data['tiempo'].iloc[-1] + 1  # Ajustar el tiempo para continuar en secuencia

# Agregar estas filas al DataFrame combinado
final_data = pd.concat([combined_data, extra_rows], ignore_index=True)

# Guardar el archivo resultante
output_path_combined = './csv/2_channel.csv'
final_data.to_csv(output_path_combined, index=False)

output_path_combined
