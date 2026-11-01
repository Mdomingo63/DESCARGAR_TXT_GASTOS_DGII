import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

def consolidar_txts_en_excel(ruta_carpeta="C:/Users/Domingo Sánchez/Escritorio/DOCUMENTOS TRABAJOS/CONTABILIDAD/DATOS EDISON/GASTOS_TXT"):
    """
    Lee todos los archivos .txt de la carpeta especificada, omite el encabezado,
    extrae columnas, agrega MES, formatea fechas y números, y guarda en Excel.
    """
    datos_totales = []
    
    # Columnas deseadas (índices basados en 0):
    # Col 1 (RNC) -> indice 0
    # Col 4 (NCF) -> indice 3
    # Col 6 (FECHA) -> indice 5
    # Col 10 (MONTO) -> indice 9
    # Col 11 (ITBIS) -> indice 10
    columnas_nombres = ['RNC', 'NCF', 'FECHA', 'MONTO', 'ITBIS']

    archivos_txt = [f for f in os.listdir(ruta_carpeta) if f.endswith('.txt')]
    
    if not archivos_txt:
        print("No se encontraron archivos .txt para procesar.")
        return

    print(f"Iniciando procesamiento de {len(archivos_txt)} archivos...")

    for archivo in archivos_txt:
        ruta_completa = os.path.join(ruta_carpeta, archivo)
        try:
            with open(ruta_completa, 'r', encoding='latin-1') as f:
                lineas = f.readlines()
                
                # Omitir la primera línea (encabezado del archivo 606|...)
                for linea in lineas[1:]:
                    linea = linea.strip()
                    if not linea: continue # Saltar líneas vacías
                    
                    partes = linea.split('|')
                    
                    # Validar que tenga suficientes columnas (al menos 11 para llegar al índice 10)
                    if len(partes) >= 11:
                        fila = {
                            'RNC': partes[0],
                            'NCF': partes[3],
                            'FECHA': partes[5],
                            'MONTO': float(partes[9]) if partes[9] else 0.0,
                            'ITBIS': float(partes[10]) if partes[10] else 0.0
                        }
                        datos_totales.append(fila)
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

    if datos_totales:
        # Crear DataFrame
        df = pd.DataFrame(datos_totales, columns=columnas_nombres)

        # Convertir columna FECHA a datetime para poder extraer el mes y dar formato
        df['FECHA'] = pd.to_datetime(df['FECHA'], format='%Y%m%d', errors='coerce')

        # Diccionario para mapear número de mes a nombre en español
        meses_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
                    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

        # Crear columna MES basada en la fecha
        df['MES'] = df['FECHA'].dt.month.map(meses_es)

        # Reordenar columnas: RNC, MES, NCF, FECHA, MONTO, ITBIS
        df = df[['RNC', 'MES', 'NCF', 'FECHA', 'MONTO', 'ITBIS']]
        
        # Definir nombre del archivo de salida
        archivo_salida = os.path.join(ruta_carpeta, "Resumen_Gastos_Consolidado.xlsx")
        
        # Guardar en Excel
        df.to_excel(archivo_salida, index=False, sheet_name="Gastos")
        
        # Aplicar formato de Tabla usando openpyxl
        wb = load_workbook(archivo_salida)
        ws = wb["Gastos"]
        
        # Definir el rango de la tabla
        # Ahora tenemos 6 columnas (hasta la F)
        rango_tabla = f"A1:F{len(datos_totales) + 1}"
        
        tabla = Table(displayName="TablaGastos", ref=rango_tabla)
        estilo = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                                showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        tabla.tableStyleInfo = estilo
        ws.add_table(tabla)

        # Dar formato a las celdas y ancho a las columnas
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            ws.column_dimensions[col].width = 18  # Aumentar ancho de columnas

        # Recorrer las filas para aplicar formatos de número y fecha
        # Fila 1 es encabezado, empezamos desde la 2
        for row in range(2, len(datos_totales) + 2):
            # Columna D (4) es FECHA -> Formato ddmmyyyy
            cell_fecha = ws.cell(row=row, column=4)
            cell_fecha.number_format = 'ddmmyyyy'
            
            # Columna E (5) MONTO y F (6) ITBIS -> Formato millares
            ws.cell(row=row, column=5).number_format = '#,##0.00'
            ws.cell(row=row, column=6).number_format = '#,##0.00'
        
        wb.save(archivo_salida)
        print(f"Proceso completado. Archivo guardado en: {archivo_salida}")
    else:
        print("No se extrajeron datos válidos de los archivos.")

if __name__ == "__main__":
    # Al ejecutar este script directamente, consolidará los TXT de la carpeta de Leyni Rodriguez
    consolidar_txts_en_excel()