import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FROM_YEAR = "2024"

def fetch_html_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
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

    # Extract version from the banner
    banner = soup.find("div", class_="header-text")
    if banner:
        version = banner.find("h2").text.strip()
        car_details["Version"] = version

    return car_details

def parse_used_car_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    car_details = {}

    # Extract version and year from the header text
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

    # Extract price in dollars
    price_in_dollars = car_header.find("h3").text.strip().replace("$", "").replace("*", "").strip()
    car_details["Precio"] = f"${price_in_dollars}"

    # Extract other car details from the table
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
            print(f"Fetching details for {'USED' if is_used else 'NEW'} car ID {car_id}")
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
    print(f"Data successfully saved to {filename}")

def fetch_new_car_ids():
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the relative path to the ChromeDriver executable
    chromedriver_path = os.path.join(current_dir, "chromedriver-mac-arm64/chromedriver")

    # Print paths for debugging
    print(f"Using ChromeDriver path: {chromedriver_path}")

    # Initialize the WebDriver with custom Chrome binary
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # Open the CRautos website
    driver.get("https://crautos.com/autosnuevos/")

    # Wait for the page to load
    time.sleep(5)  # You can use explicit waits instead of sleep

    # Scroll to the "Buscar" button to ensure it's visible
    buscar_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/section[3]/div/div/div/div/form/table/tbody/tr[8]/td/input"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", buscar_button)

    # Wait for a moment to ensure the scroll has happened
    time.sleep(1)

    # Click on the "Buscar" button to get all new cars
    buscar_button.click()

    # Wait for the results page to load
    time.sleep(3)  # Wait for 3 seconds after clicking the "Buscar" button

    # Print the title of the page to verify
    print(driver.title)

    # Scrape car IDs
    car_elements = driver.find_elements(By.CLASS_NAME, 'dealerhlcar')
    car_ids = []

    for car in car_elements:
        href = car.get_attribute('href')
        car_id = href.split('=')[1]
        car_ids.append(car_id)

    # Print the car IDs and the total count
    print(f"Total number of car IDs extracted: {len(car_ids)}")
    print(car_ids)

    # Close the WebDriver
    driver.quit()

    return car_ids

def fetch_used_car_ids():
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the relative path to the ChromeDriver executable
    chromedriver_path = os.path.join(current_dir, "chromedriver-mac-arm64/chromedriver")

    # Print paths for debugging
    print(f"Using ChromeDriver path: {chromedriver_path}")

    # Initialize the WebDriver with custom Chrome binary
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)

    # Open the CRautos website
    driver.get("https://crautos.com/autosusados/")

    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[1]/td[2]/select'))
    )

    # Select FROM_YEAR in the dropdown
    from_year_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[1]/td[2]/select'))
    from_year_dropdown.select_by_value(FROM_YEAR)

    # Select "Año" in the sort dropdown
    sort_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[5]/td[2]/select'))
    sort_dropdown.select_by_visible_text("Año")

    # Select "Solo usados" in the relevant dropdown
    solo_usados_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[6]/td[2]/select'))
    solo_usados_dropdown.select_by_visible_text("Solo usados")

    # Scroll to the "Buscar" button to ensure it's visible
    buscar_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="searchform"]/div/div[2]/table/tbody/tr[8]/td/button'))
    )
    driver.execute_script("arguments[0].scrollIntoView();", buscar_button)

    # Wait for a moment to ensure the scroll has happened
    time.sleep(1)

    # Click on the "Buscar" button to get all used cars
    buscar_button.click()

    # Wait for the results page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'brandtitle'))
    )

    # Print the title of the page to verify
    print(driver.title)

    # Scrape car IDs
    car_ids = []

    while True:
        car_elements = driver.find_elements(By.CLASS_NAME, 'brandtitle')
        for car in car_elements:
            href = car.find_element(By.TAG_NAME, 'a').get_attribute('href')
            car_id = href.split('=')[1].split('&')[0]
            car_ids.append(car_id)

        # Check for next page button
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.page-item.page-next a'))
            )
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(1)  # Ensure the scroll has happened
            driver.execute_script("arguments[0].click();", next_button)

            # Wait for the next page to load
            WebDriverWait(driver, 10).until(
                EC.staleness_of(car_elements[0])
            )
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'brandtitle'))
            )
        except Exception as e:
            print(f"No more pages. Exception: {e}")
            break

        # Print the car IDs and the total count
    print(f"Total number of car IDs extracted: {len(car_ids)}")
    print(car_ids)

    # Close the WebDriver
    driver.quit()

    return car_ids


def merge_dataframes(new_car_details, used_car_details, filename):
    # Create DataFrames
    new_cars_df = pd.DataFrame(new_car_details)
    used_cars_df = pd.DataFrame(used_car_details)

    # Standardize the column names
    new_cars_df.rename(columns={
        "Versión": "Version",
        "Precio": "Precio",
        "Año": "Año",
        "# de puertas": "Número de Puertas"
    }, inplace=True)

    used_cars_df.rename(columns={
        "# de pasajeros": "Número de Pasajeros",
        "Transmisión": "Transmisión",
        "# de puertas": "Número de Puertas",
        "Color exterior": "Color Exterior",
        "Color interior": "Color Interior",
        "Precio": "Precio",
        "Año": "Año",
        "Car ID": "Car ID"
    }, inplace=True)

    # Add a column to differentiate new and used cars
    new_cars_df['Type'] = 'Nuevo'
    used_cars_df['Type'] = 'Usado'

    # Find common columns and ensure unique column names
    common_columns = set(new_cars_df.columns).intersection(set(used_cars_df.columns))
    new_cars_df = new_cars_df.rename(columns={col: f"{col}_new" for col in common_columns if col != 'Car ID'})
    used_cars_df = used_cars_df.rename(columns={col: f"{col}_used" for col in common_columns if col != 'Car ID'})

    # Concatenate DataFrames, filling NaNs for missing columns
    combined_df = pd.concat([new_cars_df, used_cars_df], ignore_index=True, sort=False)

    # Save to Excel
    combined_df.to_excel(filename, index=False)
    print(f"Combined data successfully saved to {filename}")



def main():
    # Fetch and save new car details
    new_car_ids = fetch_new_car_ids()
    new_car_details_list = fetch_car_details(new_car_ids,
                                             "https://crautos.com/autosnuevos/cardetail.cfm?c=")
    save_to_excel(new_car_details_list, 'new_car_details.xlsx')

    # Fetch and save used car details
    used_car_ids = fetch_used_car_ids()
    used_car_details_list = fetch_car_details(used_car_ids,
                                              "https://crautos.com/autosusados/cardetail.cfm?c=",
                                              is_used=True)
    save_to_excel(used_car_details_list, 'used_car_details.xlsx')

    # Merge dataframes and save to a combined Excel file
    merge_dataframes(new_car_details_list, used_car_details_list, 'combined_car_details.xlsx')


if __name__ == "__main__":
    main()
