import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import data_analysis as da

FROM_YEAR = "2020"

def fetch_html_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Fallo al obtener la página. Código de estado: {response.status_code}")
        return None

def parse_new_car_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    fichatecnica = soup.find(id="fichatecnica")
    car_details = {}

    if fichatecnica:
        rows = fichatecnica.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) == 2:
                key = columns[0].text.strip()
                value = columns[1].text.strip()
                car_details[key] = value

    # Extraer versión del banner
    banner = soup.find("div", class_="header-text")
    if banner:
        version = banner.find("h2").text.strip()
        car_details["Version"] = version

    return car_details

def parse_used_car_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    car_details = {}

    # Extraer versión y año del texto del encabezado
    header_text = soup.find("div", class_="header-text")
    if header_text:
        car_header = header_text.find("div", class_="carheader")
        if car_header:
            version_text = car_header.find("h1").text.strip()
            parts = version_text.split()
            if len(parts) >= 3:
                year = parts[-1]
                version = " ".join(parts[:-1])
                car_details["Año"] = year
                car_details["Version"] = version

            # Extraer precio en dólares o colones
            price_in_dollars_element = car_header.find("h3")
            if price_in_dollars_element:
                price_text = price_in_dollars_element.text.strip()
                price_text = price_text.replace("(", "").replace(")", "").replace("*", "").replace("$", "").strip()
                price_text = price_text.replace(",", "")
                if "¢" in price_text:
                    # Convertir colones a dólares
                    price_in_colones = int(price_text.replace("¢", "").strip())
                    price_in_dollars = price_in_colones // 530
                    car_details["Precio"] = f"$ {price_in_dollars:,}"
                else:
                    car_details["Precio"] = f"$ {int(price_text):,}"

    # Extraer otros detalles del carro de la tabla
    tab_content = soup.find("div", class_="tab-content")
    if tab_content:
        general_info_table = tab_content.find("div", id="tab-1").find("table")
        for row in general_info_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                car_details[cells[0].text.strip()] = cells[1].text.strip()

    return car_details

def fetch_car_details(car_ids, base_url, is_used=False):
    car_details_list = []

    for car_id in car_ids:
        url = f"{base_url}{car_id}"
        html_content = fetch_html_content(url)
        if html_content:
            print(f"Obteniendo detalles para el carro {'USADO' if is_used else 'NUEVO'} con ID {car_id}")
            if is_used:
                car_details = parse_used_car_details(html_content)
            else:
                car_details = parse_new_car_details(html_content)
            car_details['Car ID'] = car_id
            car_details_list.append(car_details)

    return car_details_list

def save_to_excel(car_details_list, filename):
    df = pd.DataFrame(car_details_list)
    df.to_excel(filename, index=False)
    print(f"Datos guardados exitosamente en {filename}")

def fetch_new_car_ids():
    # Obtener el directorio actual del script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construir la ruta relativa al ejecutable de ChromeDriver
    chromedriver_path = os.path.join(current_dir, "chromedriver-mac-arm64/chromedriver")

    # Imprimir rutas para depuración
    print(f"Usando la ruta de ChromeDriver: {chromedriver_path}")

    # Inicializar el WebDriver con el binario de Chrome personalizado
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # Abrir el sitio web de CRautos
    driver.get("https://crautos.com/autosnuevos/")

    # Esperar a que la página cargue
    time.sleep(5)  # Puedes usar esperas explícitas en lugar de sleep

    # Desplazarse hasta el botón "Buscar" para asegurarse de que sea visible
    buscar_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/section[3]/div/div/div/div/form/table/tbody/tr[8]/td/input"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", buscar_button)

    # Esperar un momento para asegurarse de que el desplazamiento ha ocurrido
    time.sleep(1)

    # Hacer clic en el botón "Buscar" para obtener todos los carros nuevos
    buscar_button.click()

    # Esperar a que la página de resultados cargue
    time.sleep(3)  # Esperar 3 segundos después de hacer clic en el botón "Buscar"

    # Imprimir el título de la página para verificar
    print(driver.title)

    # Extraer los IDs de los carros
    car_elements = driver.find_elements(By.CLASS_NAME, 'dealerhlcar')
    car_ids = []

    for car in car_elements:
        href = car.get_attribute('href')
        car_id = href.split('=')[1]
        car_ids.append(car_id)

    # Imprimir los IDs de los carros y el total
    print(f"Total de IDs de carros extraídos: {len(car_ids)}")
    print(car_ids)

    # Cerrar el WebDriver
    driver.quit()

    return car_ids

def fetch_used_car_ids():
    # Obtener el directorio actual del script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construir la ruta relativa al ejecutable de ChromeDriver
    chromedriver_path = os.path.join(current_dir, "chromedriver-mac-arm64/chromedriver")

    # Imprimir rutas para depuración
    print(f"Usando la ruta de ChromeDriver: {chromedriver_path}")

    # Inicializar el WebDriver con el binario de Chrome personalizado
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # Abrir el sitio web de CRautos
    driver.get("https://crautos.com/autosusados/")

    # Esperar a que la página cargue
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[1]/td[2]/select'))
    )

    # Seleccionar FROM_YEAR en el menú desplegable
    from_year_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[1]/td[2]/select'))
    from_year_dropdown.select_by_value(FROM_YEAR)

    # Seleccionar "Año" en el menú desplegable de orden
    sort_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[5]/td[2]/select'))
    sort_dropdown.select_by_visible_text("Año")

    # Seleccionar "Solo usados" en el menú desplegable relevante
    solo_usados_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[6]/td[2]/select'))
    solo_usados_dropdown.select_by_visible_text("Solo usados")

    # Desplazarse hasta el botón "Buscar" para asegurarse de que sea visible
    buscar_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[8]/td/button'))
    )
    driver.execute_script("arguments[0].scrollIntoView();", buscar_button)

    # Esperar un momento para asegurarse de que el desplazamiento ha ocurrido
    time.sleep(1)

    # Hacer clic en el botón "Buscar" para obtener todos los carros usados
    buscar_button.click()

    # Esperar a que la página de resultados cargue
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'brandtitle'))
    )

    # Imprimir el título de la página para verificar
    print(driver.title)

    # Extraer los IDs de los carros
    car_ids = []

    while True:
        car_elements = driver.find_elements(By.CLASS_NAME, 'brandtitle')
        for car in car_elements:
            href = car.find_element(By.TAG_NAME, 'a').get_attribute('href')
            car_id = href.split('=')[1].split('&')[0]
            car_ids.append(car_id)

        # Verificar si hay un botón de página siguiente
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.page-item.page-next a'))
            )
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(1)  # Asegurarse de que el desplazamiento ha ocurrido
            driver.execute_script("arguments[0].click();", next_button)

            # Esperar a que la siguiente página cargue
            WebDriverWait(driver, 10).until(
                EC.staleness_of(car_elements[0])
            )
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'brandtitle'))
            )
        except Exception as e:
            print(f"No hay más páginas. Excepción: {e}")
            break

    # Imprimir los IDs de los carros y el total
    print(f"Total de IDs de carros extraídos: {len(car_ids)}")
    print(car_ids)

    # Cerrar el WebDriver
    driver.quit()

    return car_ids


def merge_dataframes(new_car_details, used_car_details, filename):
    # Crear DataFrames
    new_cars_df = pd.DataFrame(new_car_details)
    used_cars_df = pd.DataFrame(used_car_details)

    # Concatenar DataFrames, llenando NaNs para columnas faltantes
    combined_df = pd.concat([new_cars_df, used_cars_df], ignore_index=True, sort=False)

    # Guardar en Excel
    combined_df.to_excel(filename, index=False)
    print(f"Datos combinados guardados exitosamente en {filename}")


def main():
    # Obtener y guardar detalles de carros nuevos
    new_car_ids = fetch_new_car_ids()
    new_car_details_list = fetch_car_details(new_car_ids,
                                             "https://crautos.com/autosnuevos/cardetail.cfm?c=")
    save_to_excel(new_car_details_list, 'new_car_details.xlsx')

    # Obtener y guardar detalles de carros usados
    used_car_ids = fetch_used_car_ids()
    used_car_details_list = fetch_car_details(used_car_ids,
                                              "https://crautos.com/autosusados/cardetail.cfm?c=",
                                              is_used=True)
    save_to_excel(used_car_details_list, 'used_car_details.xlsx')

    # Fusionar dataframes y guardar en un archivo Excel combinado
    merge_dataframes(new_car_details_list, used_car_details_list, 'combined_car_details.xlsx')

    # Cargar y limpiar los datos combinados
    combined_df = da.load_data('combined_car_details.xlsx')
    combined_df = da.clean_data(combined_df)

    # Graficar tendencias
    da.plot_average_price_by_year(combined_df)
    da.plot_most_common_models(combined_df, top_n=10)


if __name__ == "__main__":
    main()

