from dotenv import load_dotenv
load_dotenv()
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import os
import shutil
from procesarTxtAExcel import consolidar_txts_en_excel

def descarga_Txt606_periodo_especifico(usuario: str, clave: str, periodo_deseado: str, anio: str):
    """ Automatiza el inicio de sesión y descarga el txt de gastos para un 
    período específico en la DGII.
    """
    # Inicializar el navegador
    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://dgii.gov.do/OFV/login.aspx")

        # Ingreso de credenciales

        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtUsuario"))).send_keys(usuario)
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtPassword").send_keys(clave)
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_BtnAceptar").click()

        # Esperar la carga del menú y hacer click en la opción
        wait.until(EC.element_to_be_clickable((By.ID, "2194"))).click()

        # Seleccionar el año en el desplegable
        seleccion_elemento = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_lstPeriodo"]')))
        seleccion = Select(seleccion_elemento)
        # Seleccionamos por el texto del año en vez de por índice
        seleccion.select_by_visible_text(str(anio))

        # Buscar los datos 
        wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnBuscar" ))).click()

        # Esperar la tabla y obtener las filas

        tabla = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_dgFuente"]')))
        filas = tabla.find_elements(By.XPATH, './/tr')

        # Iterar sobre las filas de la tabla omitiendo el encabezado
        for fila in filas[1:]:
            try:
                periodo_texto =  fila.find_element(By.XPATH, './td[2]').text.strip()

                if periodo_texto == periodo_deseado:
                    enlace_descarga = fila.find_element(By.XPATH, './td[1]/a')
                    print(f"Descargando archivo para el período: {periodo_texto}")
                    enlace_descarga.click()
                    time.sleep(5)

                    # Detiene el bucle después de encontrar el período deseado
                    break
            except Exception as e:
                print(f"Error en la fila: {e}") 

        # Cerrar sesión           
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menus"]/li[5]/a' ))).click()

        carpeta_descarga = os.path.join(os.path.expanduser("~"), "Downloads")
        carpeta_destino = "C:/Users/Domingo Sánchez/Escritorio/DOCUMENTOS TRABAJOS/CONTABILIDAD/DATOS EDISON/GASTOS_TXT"

        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)

        for archivo in os.listdir(carpeta_descarga):
            if archivo.endswith('.txt'):
                ruta_archivo_origen = os.path.join(carpeta_descarga, archivo)
                ruta_archivo_destino = os.path.join(carpeta_destino, archivo)
                shutil.move(ruta_archivo_origen, ruta_archivo_destino)

        # Una vez movido el archivo, ejecutamos la consolidación automática
        print("Iniciando consolidación en Excel...")
        consolidar_txts_en_excel(carpeta_destino)
    finally:
        driver.quit()

# Desde aquí se llama a la función y se le pasan los parámetros
descarga_Txt606_periodo_especifico(os.getenv("USUARIO_DGII"), os.getenv("CLAVE_DGII"), "202403", "2024")
