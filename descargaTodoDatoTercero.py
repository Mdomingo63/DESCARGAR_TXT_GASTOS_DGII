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
import os
from time import sleep
import shutil

def descarga_Txt606_periodo_especifico(usuario: str, clave: str, indice_anio: int):
    """ Automatiza el inicio de sesión y descarga el txt de gastos para un 
    período específico en la DGII.
    Nota: antes de ejecutar este código debe verificar la carpeta_destino, el usuario, clave y el indice_anio
    para ver si coinciden con el contribuyente que desea descargarles los datos.
    """
    # Inicializar el navegador
    service = Service(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

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
            WebDriverWait(driver, 60).until(lambda driver: token_field.get_attribute("value") != "")
            sleep(15) 
             # Hacer clic en el botón "Continuar" automáticamente
            continuar_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_BtnAceptarTarjetaToken"]')))
            continuar_button.click()
            print("Token ingresado y botón 'Continuar' presionado automáticamente.")

            # Esperar a que el link de la siguiente página aparezca
            siguiente_link = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "2231")))  # ID del enlace al que hay que hacer clic)
            # Hacer clic en el enlace después del login
            siguiente_link.click()
            print("Se hizo clic en el enlace después del login.")

        except NoSuchElementException:
            print("El campo de token o el enlace no están presentes, continuando sin ellos.")


        # Seleccionar el año en el desplegable
        seleccion_elemento = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_dplYearFiscal"]')))
        seleccion = Select(seleccion_elemento)
        seleccion.select_by_index(indice_anio)

    
        # Hacer click en la primera tabla resumen de tarjeta terceros y 606 terceros

        tabla_resumen = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_tblResumen"]')))
        filas_resumen = tabla_resumen.find_elements(By.XPATH, './/tr')

        valor_fila1_columna2 = float(filas_resumen[1].find_elements(By.TAG_NAME, "td")[1].text.replace(',', ''))  # Convertir a flotante y manejar comas
        valor_fila2_columna2 = float(filas_resumen[2].find_elements(By.TAG_NAME, "td")[1].text.replace(',', ''))  # Convertir a flotante y manejar comas
 

        for fila in filas_resumen[1:]:
            try:
                if valor_fila1_columna2 > 0:
                    # Hacer clic en el botón "Ingresos Tarjetas" y esperar a que se cargue la siguiente sección
                    driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnIngresosTarjetas"]').click()
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnDescargarTodo"]'))).click()
                
                    # Esperar que el botón "Atras" esté disponible después de que la página se haya cargado
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnAtras"]'))).click()
                    
                if valor_fila2_columna2 > 0:
                    # Hacer clic en el botón "Ingresos 606" y esperar a que se cargue la siguiente sección
                    boton_ingreso_606 = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnIngresos606"]')))
                    boton_ingreso_606.click()
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnDescargarTodo"]'))).click()
                
                    # Esperar que el botón "Atras" esté disponible después de que la página se haya cargado
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_btnAtras"]'))).click()
                    break
                
            except Exception as e:
                print(f'Error al hacer click en elemento: {e}')


        # Cerrar sesión           
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="menus"]/li[5]/a' ))).click()

        carpeta_descarga = "C:/Users/Domingo Sánchez/Downloads"
        carpeta_destino = "C:/Users/Domingo Sánchez/Escritorio/DOCUMENTOS TRABAJOS/CONTABILIDAD/DATOS EDISON/INGRESOS_TERCEROS_607"

        for archivo in os.listdir(carpeta_descarga):
            if archivo.endswith('.xls'):
                ruta_archivo_origen = os.path.join(carpeta_descarga, archivo)
                ruta_archivo_destino = os.path.join(carpeta_destino, archivo)
                shutil.move(ruta_archivo_origen, ruta_archivo_destino)
    finally:
        driver.quit()

# Desde aquí se llama a la función y se le pasan los parámetros
usuario_dgii = os.getenv("USUARIO_DGII")
clave_dgii = os.getenv("CLAVE_DGII")
if not usuario_dgii or not clave_dgii:
    raise ValueError("Faltan las variables de entorno USUARIO_DGII o CLAVE_DGII")
descarga_Txt606_periodo_especifico(usuario_dgii, clave_dgii, 2)
