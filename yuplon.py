import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import data_analysis as da

def extract_campaign_details(driver):
    # Extract the main offer title
    main_offer = driver.find_element(By.CSS_SELECTOR, "span.text-3xl").text

    # Extract additional details using provided XPaths
    calificacion = driver.find_element(By.XPATH,
                                       "//*[@id='root']/div[4]/section/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/span").text
    vendidas = driver.find_element(By.XPATH,
                                   "//*[@id='root']/div[4]/section/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/span").text

    valido_para_redimir_text = driver.find_element(By.XPATH,
                                                   "//*[@id='root']/div[4]/section/div[1]/div[3]/div[3]/div/ol/li[1]").text
    # Handling different date formats
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
        # Handle other date format
        start_date = end_date = valido_para_redimir_text.split(" ")[-1].strip().split(".")[0]

    # Extract sub-offer details
    sub_offers_elements = driver.find_elements(By.CSS_SELECTOR, "div.pb-10")
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

def main():
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the relative path to the ChromeDriver executable
    chromedriver_path = os.path.join(current_dir, "chromedriver-mac-arm64/chromedriver")

    # Print paths for debugging
    print(f"Using ChromeDriver path: {chromedriver_path}")

    # Initialize the WebDriver with custom Chrome binary
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)


    try:
        # Open the Yuplon website
        driver.get("https://www.yuplon.com/")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "grid-cols-1"))
        )

        # Scroll to load more items if needed
        last_height = driver.execute_script("return document.body.scrollHeight")
        details_links = set()

        while True:
            # Scroll to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Adjust this if necessary for the site to load more items

            # Find all 'Ver Detalles' links
            details_elements = driver.find_elements(By.XPATH,
                                                    "//a[contains(text(), 'Ver Detalles')]")
            for element in details_elements:
                details_links.add(element.get_attribute('href'))

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Print the count of 'Ver Detalles' links
        print(f"Number of 'Ver Detalles' links found: {len(details_links)}")
        print(details_links)

        # Visit each link and extract campaign details
        all_campaign_data = []
        test = ['https://www.yuplon.com/campaign/5247', 'https://www.yuplon.com/campaign/5222', 'https://www.yuplon.com/campaign/5301', 'https://www.yuplon.com/campaign/5196', 'https://www.yuplon.com/campaign/5299', 'https://www.yuplon.com/campaign/5298', 'https://www.yuplon.com/campaign/5283', 'https://www.yuplon.com/campaign/5273', 'https://www.yuplon.com/campaign/5285', 'https://www.yuplon.com/campaign/5271', 'https://www.yuplon.com/campaign/5297', 'https://www.yuplon.com/campaign/5228', 'https://www.yuplon.com/campaign/5241', 'https://www.yuplon.com/campaign/5308', 'https://www.yuplon.com/campaign/5294', 'https://www.yuplon.com/campaign/5263', 'https://www.yuplon.com/campaign/5300', 'https://www.yuplon.com/campaign/5270', 'https://www.yuplon.com/campaign/5256', 'https://www.yuplon.com/campaign/5289', 'https://www.yuplon.com/campaign/5269', 'https://www.yuplon.com/campaign/5288', 'https://www.yuplon.com/campaign/5278', 'https://www.yuplon.com/campaign/5296', 'https://www.yuplon.com/campaign/5305', 'https://www.yuplon.com/campaign/5275', 'https://www.yuplon.com/campaign/5259', 'https://www.yuplon.com/campaign/5265', 'https://www.yuplon.com/campaign/5276', 'https://www.yuplon.com/campaign/5268', 'https://www.yuplon.com/campaign/5309', 'https://www.yuplon.com/campaign/5287', 'https://www.yuplon.com/campaign/5286', 'https://www.yuplon.com/campaign/5274', 'https://www.yuplon.com/campaign/5277', 'https://www.yuplon.com/campaign/5315', 'https://www.yuplon.com/campaign/5251', 'https://www.yuplon.com/campaign/5249', 'https://www.yuplon.com/campaign/5312', 'https://www.yuplon.com/campaign/5279', 'https://www.yuplon.com/campaign/5224', 'https://www.yuplon.com/campaign/5266', 'https://www.yuplon.com/campaign/5306', 'https://www.yuplon.com/campaign/5272', 'https://www.yuplon.com/campaign/5311', 'https://www.yuplon.com/campaign/4977', 'https://www.yuplon.com/campaign/5284', 'https://www.yuplon.com/campaign/5302', 'https://www.yuplon.com/campaign/5295', 'https://www.yuplon.com/campaign/5227', 'https://www.yuplon.com/campaign/5250', 'https://www.yuplon.com/campaign/5282', 'https://www.yuplon.com/campaign/5238', 'https://www.yuplon.com/campaign/5257', 'https://www.yuplon.com/campaign/5174', 'https://www.yuplon.com/campaign/5316', 'https://www.yuplon.com/campaign/5211', 'https://www.yuplon.com/campaign/5242', 'https://www.yuplon.com/campaign/5261', 'https://www.yuplon.com/campaign/5267', 'https://www.yuplon.com/campaign/5264', 'https://www.yuplon.com/campaign/5319', 'https://www.yuplon.com/campaign/5304', 'https://www.yuplon.com/campaign/5317', 'https://www.yuplon.com/campaign/5314', 'https://www.yuplon.com/campaign/5281']
        for link in test:
            print(f"Obteniendo detalles de oferta: {link}")
            driver.get(link)
            time.sleep(5)  # Wait for the page to load fully
            campaign_data = extract_campaign_details(driver)
            all_campaign_data.extend(campaign_data)

        # Save the campaign data to an Excel file
        df = pd.DataFrame(all_campaign_data)
        df.to_excel('campaign_data.xlsx', index=False)
        print("Campaign details saved to campaign_data.xlsx")

        # Graficar tendencias
        campaign_data = da.load_data('campaign_data.xlsx')
        campaign_data = da.clean_data_yuplon(campaign_data)
        da.plot_most_discount_offers(campaign_data)
        da.plot_relation_price_vendidas_discount(campaign_data)
        da.plot_least_discount_offers(campaign_data)
        da.plot_most_expensive_offers(campaign_data)
        da.plot_least_expensive_offers(campaign_data)

    finally:
        # Close the WebDriver
        driver.quit()


if __name__ == "__main__":
    main()
