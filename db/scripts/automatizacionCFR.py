import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def buscar_cfr(nombre_buque):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://servicio.pesca.mapama.es/censo/ConsultaBuqueRegistro/Buques/Search")
        wait = WebDriverWait(driver, 15)

        # Buscar el campo y enviar nombre
        input_nombre = wait.until(EC.presence_of_element_located((By.ID, "text")))
        input_nombre.send_keys(nombre_buque)

        # Hacer clic en buscar
        boton = driver.find_element(By.CSS_SELECTOR, "button.btn")
        boton.click()

        # Esperar a que aparezca el texto "resultados encontrados" (confirmación)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".txt--items-found-count")))

        # Buscar directamente el span que contiene el CFR
        cfr_span = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[contains(text(), 'CFR:')]/following-sibling::span")
        ))

        cfr = cfr_span.text.strip()
        print("✅ CFR encontrado:", cfr)
        return cfr

    except Exception as e:
        print("❌ Error:", e)
        return "No se encontró ningún resultado"

    finally:
        time.sleep(2)
        driver.quit()


# Leer el archivo Excel
excel_path = "C:/Users/cgmoy/Desktop/IO/LICENCIAS_CFR_MODIFICADO.xlsx" # Cambia esto por la ruta de tu archivo
df = pd.read_excel(excel_path, sheet_name=1)  # Leemos la segunda hoja (index 1)

# Filtrar las filas donde el CFR está vacío
buques_sin_cfr = df[df['CodigoCFR'].isnull()]

# Para cada buque sin CFR, buscarlo y agregar el CFR
for index, row in buques_sin_cfr.iterrows():
    nombre_buque = row['BUQUE']  
    print(f"Buscando CFR para el buque: {nombre_buque}")
    cfr = buscar_cfr(nombre_buque)
    
    # Actualizar el DataFrame con el nuevo CFR
    df.loc[index, 'CodigoCFR'] = cfr

# Guardar el DataFrame actualizado de nuevo al archivo Excel
df.to_excel("archivo_actualizado.xlsx", index=False)

print("✅ Proceso completado, archivo guardado como 'archivo_actualizado.xlsx'")
