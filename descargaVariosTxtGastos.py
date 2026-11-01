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
from selenium.common.exceptions import NoSuchElementException
import time
import os
import shutil
from procesarTxtAExcel import consolidar_txts_en_excel

def descargar_Txt606(usuario: str, clave: str, anio: str):
    """Automatiza el inicio de sesión y descarga los txt de gastos de todo un año en la DGII."""
    
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
        try:
            token_field = driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_txtpasscodeTarjetaToken"]')
            print("Por favor, ingrese el token en la página (NO presione Enter). El sistema continuará automáticamente.")

            # Esperar a que el usuario ingrese el token (sin presionar Enter)
            WebDriverWait(driver, 60).until(lambda d: token_field.get_attribute("value") != "")
            time.sleep(15) 
            # Hacer clic en el botón "Continuar" automáticamente
            continuar_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_BtnAceptarTarjetaToken"]')))
            continuar_button.click()
            print("Token ingresado y botón 'Continuar' presionado automáticamente.")

        except NoSuchElementException:
            print("El campo de token o el enlace no están presentes, continuando sin ellos.")
        
        # Esperar la carga del menú y hacer clic en la opción
        wait.until(EC.element_to_be_clickable((By.ID, "2194"))).click()
        
        # Seleccionar periodo fiscal
        seleccion_elemento = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_lstPeriodo"]')))
        seleccion = Select(seleccion_elemento)
        
        # Seleccionamos el año directamente por su texto visible (ej. "2026")
        seleccion.select_by_visible_text(str(anio))
        
        # Buscar datos
        wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnBuscar"))).click()
        
        # Esperar la tabla y obtener las filas
        tabla = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_dgFuente"]')))
        filas = tabla.find_elements(By.XPATH, './/tr')

        # Iterar sobre las filas (omitimos la primera si es encabezado)
        for fila in filas[1:]:
            try:
                enlace_descarga = fila.find_element(By.XPATH, './td[1]/a')  # Link de descarga
                periodo_texto = fila.find_element(By.XPATH, './td[2]').text.strip()  # Periodo
                
                print(f"Descargando archivo para periodo: {periodo_texto}")
                enlace_descarga.click()
                time.sleep(5)  # Esperar un poco para la descarga
                
            except Exception as e:
                print(f"Error en la fila: {e}")

        # Cerrar sesión
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menus"]/li[5]/a'))).click()
        
        carpeta_descarga = os.path.join(os.path.expanduser("~"), "Downloads")
        carpeta_destino = "C:/Users/Domingo Sánchez/Escritorio/DOCUMENTOS TRABAJOS/CONTABILIDAD/DATOS EDISON/GASTOS_TXT"
        
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)

        for archivo in os.listdir(carpeta_descarga):
            # Filtrar solo archivos .txt que empiecen con "606" y eliminarles la extensión
            nombre_sin_extension = os.path.splitext(archivo)[0]
            if archivo.endswith('.txt') and nombre_sin_extension.startswith('606'):
                ruta_archivo_origen = os.path.join(carpeta_descarga, archivo)
                ruta_archivo_destino = os.path.join(carpeta_destino, archivo)
                shutil.move(ruta_archivo_origen, ruta_archivo_destino)
                print(f"Archivo movido: {archivo}")

        # Una vez movidos los archivos filtrados, ejecutamos el procesamiento a Excel
        print("Iniciando consolidación en Excel...")
        consolidar_txts_en_excel(carpeta_destino)

    finally:
        driver.quit()


# Uso de la función dentro del bloque main para evitar ejecución al importar
if __name__ == "__main__":
    # Ahora pasamos el año directamente como una cadena de texto
    usuario_dgii = os.getenv("USUARIO_DGII")
    clave_dgii = os.getenv("CLAVE_DGII")
    if not usuario_dgii or not clave_dgii:
        raise ValueError("Faltan las variables de entorno USUARIO_DGII o CLAVE_DGII")
    descargar_Txt606(usuario_dgii, clave_dgii, "2026")
