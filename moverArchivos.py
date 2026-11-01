import os
import shutil

carpeta_descarga = os.path.join(os.path.expanduser("~"), "Downloads")
carpeta_destino = "C:/Users/Domingo Sánchez/Escritorio/DOCUMENTOS TRABAJOS/CONTABILIDAD/DATOS EDISON/GASTOS_TXT"

for archivo in os.listdir(carpeta_descarga):
    if archivo.endswith('.txt'):
        ruta_archivo_origen = os.path.join(carpeta_descarga, archivo)
        ruta_archivo_destino = os.path.join(carpeta_destino, archivo)
        shutil.move(ruta_archivo_origen, ruta_archivo_destino)

print(f'Archivos movidos a la carpeta: {carpeta_destino}')          