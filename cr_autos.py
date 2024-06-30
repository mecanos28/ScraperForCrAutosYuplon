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

class WebScraper:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        # Inicializar el WebDriver con el binario de Chrome personalizado
        service = ChromeService(executable_path=self.driver_path)
        driver = webdriver.Chrome(service=service)
        return driver

    def open_website(self, url):
        # Abrir el sitio web
        self.driver.get(url)

    def wait_for_element(self, by, value, timeout=10):
        # Esperar a que un elemento esté presente en la página
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def close_driver(self):
        # Cerrar el WebDriver
        self.driver.quit()

class CarDetailsFetcher:
    @staticmethod
    def fetch_html_content(url):
        # Obtener el contenido HTML de una URL
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Fallo al obtener la página. Código de estado: {response.status_code}")
            return None

    @staticmethod
    def parse_new_car_details(html_content):
        # Parsear detalles de un carro nuevo
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

        banner = soup.find("div", class_="header-text")
        if banner:
            version = banner.find("h2").text.strip()
            car_details["Version"] = version

        return car_details

    @staticmethod
    def parse_used_car_details(html_content):
        # Parsear detalles de un carro usado
        soup = BeautifulSoup(html_content, 'html.parser')
        car_details = {}

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

                price_in_dollars_element = car_header.find("h3")
                if price_in_dollars_element:
                    price_text = price_in_dollars_element.text.strip()
                    price_text = price_text.replace("(", "").replace(")", "").replace("*", "").replace("$", "").strip()
                    price_text = price_text.replace(",", "")
                    if "¢" in price_text:
                        price_in_colones = int(price_text.replace("¢", "").strip())
                        price_in_dollars = price_in_colones // 530
                        car_details["Precio"] = f"$ {price_in_dollars:,}"
                    else:
                        car_details["Precio"] = f"$ {int(price_text):,}"

        tab_content = soup.find("div", class_="tab-content")
        if tab_content:
            general_info_table = tab_content.find("div", id="tab-1").find("table")
            for row in general_info_table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) == 2:
                    car_details[cells[0].text.strip()] = cells[1].text.strip()

        return car_details

    @staticmethod
    def fetch_car_details(car_ids, base_url, is_used=False):
        # Obtener detalles de los carros
        car_details_list = []

        for car_id in car_ids:
            url = f"{base_url}{car_id}"
            html_content = CarDetailsFetcher.fetch_html_content(url)
            if html_content:
                print(f"Obteniendo detalles para el carro {'USADO' if is_used else 'NUEVO'} con ID {car_id}")
                if is_used:
                    car_details = CarDetailsFetcher.parse_used_car_details(html_content)
                else:
                    car_details = CarDetailsFetcher.parse_new_car_details(html_content)
                car_details['Car ID'] = car_id
                car_details_list.append(car_details)

        return car_details_list

class DataManager:
    @staticmethod
    def save_to_excel(data, filename):
        # Guardar los datos en un archivo Excel
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"Datos guardados exitosamente en {filename}")

    @staticmethod
    def merge_dataframes(new_car_details, used_car_details, filename):
        # Fusionar DataFrames y guardar en un archivo Excel
        new_cars_df = pd.DataFrame(new_car_details)
        used_cars_df = pd.DataFrame(used_car_details)
        combined_df = pd.concat([new_cars_df, used_cars_df], ignore_index=True, sort=False)
        combined_df.to_excel(filename, index=False)
        print(f"Datos combinados guardados exitosamente en {filename}")

class NewCarScraper(WebScraper):
    def fetch_car_ids(self):
        # Obtener IDs de carros nuevos
        self.open_website("https://crautos.com/autosnuevos/")
        time.sleep(5)
        buscar_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/section[3]/div/div/div/div/form/table/tbody/tr[8]/td/input"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", buscar_button)
        time.sleep(1)
        buscar_button.click()
        time.sleep(3)
        print(self.driver.title)

        car_elements = self.driver.find_elements(By.CLASS_NAME, 'dealerhlcar')
        car_ids = [car.get_attribute('href').split('=')[1] for car in car_elements]

        print(f"Total de IDs de carros extraídos: {len(car_ids)}")
        print(car_ids)

        self.close_driver()
        return car_ids

class UsedCarScraper(WebScraper):
    def fetch_car_ids(self):
        # Obtener IDs de carros usados
        self.open_website("https://crautos.com/autosusados/")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[1]/td[2]/select'))
        )

        from_year_dropdown = Select(self.driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[1]/td[2]/select'))
        from_year_dropdown.select_by_value(FROM_YEAR)
        sort_dropdown = Select(self.driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[5]/td[2]/select'))
        sort_dropdown.select_by_visible_text("Año")
        solo_usados_dropdown = Select(self.driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[6]/td[2]/select'))
        solo_usados_dropdown.select_by_visible_text("Solo usados")
        buscar_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[8]/td/button'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", buscar_button)
        time.sleep(1)
        buscar_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'brandtitle'))
        )
        print(self.driver.title)

        car_ids = []
        while True:
            car_elements = self.driver.find_elements(By.CLASS_NAME, 'brandtitle')
            for car in car_elements:
                href = car.find_element(By.TAG_NAME, 'a').get_attribute('href')
                car_id = href.split('=')[1].split('&')[0]
                car_ids.append(car_id)

            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.page-item.page-next a'))
                )
                self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", next_button)
                WebDriverWait(self.driver, 10).until(
                    EC.staleness_of(car_elements[0])
                )
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'brandtitle'))
                )
            except Exception as e:
                print(f"No hay más páginas. Excepción: {e}")
                break

        print(f"Total de IDs de carros extraídos: {len(car_ids)}")
        print(car_ids)

        self.close_driver()
        return car_ids

def main():
    # Obtener el directorio actual del script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construir la ruta relativa al ejecutable de ChromeDriver
    chromedriver_path = os.path.join(current_dir, "chromedriver-mac-arm64/chromedriver")
    print(f"Usando la ruta de ChromeDriver: {chromedriver_path}")

    # Obtener y guardar detalles de carros nuevos
    new_car_scraper = NewCarScraper(driver_path=chromedriver_path)
    new_car_ids = new_car_scraper.fetch_car_ids()
    new_car_details_list = CarDetailsFetcher.fetch_car_details(new_car_ids, "https://crautos.com/autosnuevos/cardetail.cfm?c=")
    DataManager.save_to_excel(new_car_details_list, 'data/new_car_details.xlsx')

    # Obtener y guardar detalles de carros usados
    used_car_scraper = UsedCarScraper(driver_path=chromedriver_path)
    used_car_ids = used_car_scraper.fetch_car_ids()
    used_car_details_list = CarDetailsFetcher.fetch_car_details(used_car_ids, "https://crautos.com/autosusados/cardetail.cfm?c=", is_used=True)
    DataManager.save_to_excel(used_car_details_list, 'data/used_car_details.xlsx')

    # Fusionar DataFrames y guardar en un archivo Excel combinado
    DataManager.merge_dataframes(new_car_details_list, used_car_details_list, 'data/combined_car_details.xlsx')

    # Cargar y limpiar los datos combinados
    combined_df = da.load_data('data/combined_car_details.xlsx')
    combined_df = da.clean_data(combined_df)

    # Graficar tendencias
    da.plot_average_price_by_year(combined_df)
    da.plot_most_common_models(combined_df, top_n=10)
    da.plot_most_expensive_models(combined_df, top_n=10)
    da.plot_cheapest_models(combined_df, top_n=10)


if __name__ == "__main__":
    main()
