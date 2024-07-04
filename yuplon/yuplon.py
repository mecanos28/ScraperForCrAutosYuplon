import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import data_analysis as da

class CampaignScraper:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        # Inicializar el WebDriver con binario de Chrome personalizado
        service = ChromeService(executable_path=self.driver_path)
        driver = webdriver.Chrome(service=service)
        return driver

    def open_website(self, url):
        # Abrir el sitio web de Yuplon
        self.driver.get(url)

    def wait_for_element(self, by, value, timeout=10):
        # Esperar a que la página cargue
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def scroll_to_load_more(self):
        # Desplazarse para cargar más elementos si es necesario
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        details_links = set()

        while True:
            # Desplazarse hasta el final
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Ajustar esto si es necesario para que el sitio cargue más elementos

            # Encontrar todos los enlaces 'Ver Detalles'
            details_elements = self.driver.find_elements(By.XPATH,
                                                         "//a[contains(text(), 'Ver Detalles')]")
            for element in details_elements:
                details_links.add(element.get_attribute('href'))

            # Calcular nueva altura de desplazamiento y comparar con la última altura
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return details_links

    def extract_campaign_details(self):
        # Extraer el título de la oferta principal
        main_offer = self.driver.find_element(By.CSS_SELECTOR, "span.text-3xl").text

        # Extraer detalles adicionales usando los XPaths proporcionados
        calificacion = self.driver.find_element(By.XPATH,
                                                "//*[@id='root']/div[4]/section/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/span").text
        vendidas = self.driver.find_element(By.XPATH,
                                            "//*[@id='root']/div[4]/section/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/span").text

        valido_para_redimir_text = self.driver.find_element(By.XPATH,
                                                            "//*[@id='root']/div[4]/section/div[1]/div[3]/div[3]/div/ol/li[1]").text
        # Manejo de diferentes formatos de fecha
        if "del " in valido_para_redimir_text and " al " in valido_para_redimir_text:
            start_date = valido_para_redimir_text.split("del ")[1].split(" al ")[0].strip()
            end_date = valido_para_redimir_text.split(" al ")[1].split(".")[0].strip()
        elif " al " in valido_para_redimir_text:
            start_date = valido_para_redimir_text.split(" ")[2].split(" al ")[0].strip()
            end_date = valido_para_redimir_text.split(" al ")[1].split(".")[0].strip()
        elif "únicamente el día del evento:" in valido_para_redimir_text:
            date = valido_para_redimir_text.split("el día del evento:")[1].strip().split(".")[0]
            start_date = end_date = date
        else:
            # Manejar otro formato de fecha
            start_date = end_date = valido_para_redimir_text.split(" ")[-1].strip().split(".")[0]

        # Extraer detalles de la sub-oferta
        sub_offers_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.pb-10")
        sub_offers = []

        for sub_offer_element in sub_offers_elements:
            try:
                sub_offer_title = sub_offer_element.find_element(By.CSS_SELECTOR, "span.pb-2").text
                sub_offer_price = sub_offer_element.find_element(By.CSS_SELECTOR,
                                                                 "span.font-medium.text-2xl").text
                sub_offer_original_price = sub_offer_element.find_element(By.CSS_SELECTOR,
                                                                          "span.line-through").text
                sub_offer_discount = sub_offer_element.find_element(By.CSS_SELECTOR,
                                                                    "span.font-medium.text-2xl.text-yuplon-black.dark\:text-dark-text-primary.ml-auto.w-\[48px\]").text
                sub_offers.append({
                    'Main Offer': main_offer,
                    'Sub Offer Title': sub_offer_title,
                    'Price': sub_offer_price,
                    'Original Price': sub_offer_original_price,
                    'Discount': sub_offer_discount,
                    'Calificación': calificacion,
                    'Vendidas': vendidas,
                    'Start Date': start_date,
                    'End Date': end_date,
                })
            except Exception as e:
                print(f"Error extracting sub-offer details: {e}")

        return sub_offers

    def close_driver(self):
        # Cerrar el WebDriver
        self.driver.quit()


class DataManager:
    def __init__(self, file_name):
        self.file_name = file_name

    def save_to_excel(self, data):
        # Guardar los datos de la campaña en un archivo Excel
        df = pd.DataFrame(data)
        df.to_excel(self.file_name, index=False)
        print(f"Detalles de la campaña guardados en {self.file_name}")

    def analyze_data(self):
        # Graficar tendencias
        campaign_data = da.load_data(self.file_name)
        campaign_data = da.clean_data_yuplon(campaign_data)
        da.plot_most_discount_offers(campaign_data)
        da.plot_relation_price_vendidas_discount(campaign_data)
        da.plot_least_discount_offers(campaign_data)
        da.plot_most_expensive_offers(campaign_data)
        da.plot_least_expensive_offers(campaign_data)


def main():
    # Obtener el directorio actual del script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construir la ruta relativa al ejecutable de ChromeDriver
    chromedriver_path = os.path.join(current_dir, "../chromedriver-mac-arm64/chromedriver")

    # Imprimir rutas para depuración
    print(f"Using ChromeDriver path: {chromedriver_path}")

    scraper = CampaignScraper(driver_path=chromedriver_path)
    scraper.open_website("https://www.yuplon.com/")
    scraper.wait_for_element(By.CLASS_NAME, "grid-cols-1")

    details_links = scraper.scroll_to_load_more()

    print(f"Número de enlaces 'Ver Detalles' encontrados: {len(details_links)}")
    print(details_links)

    all_campaign_data = []
    for link in details_links:
        print(f"Obteniendo detalles de oferta: {link}")
        scraper.driver.get(link)
        time.sleep(5)  # Esperar a que la página cargue completamente
        campaign_data = scraper.extract_campaign_details()
        all_campaign_data.extend(campaign_data)

    scraper.close_driver()

    data_manager = DataManager('../data/campaign_data.xlsx')
    data_manager.save_to_excel(all_campaign_data)
    data_manager.analyze_data()


if __name__ == "__main__":
    main()
