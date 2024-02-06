# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 10:56:00 2024

@author: nithy
"""

import re
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

base_url = "https://www.immoweb.be/en/search"
house_apartment_endpoint = "/house-and-apartment"
for_sale_endpoint = "/for-sale"
country_BE_endpoint = "?countries=BE"
life_annuity_endpoint = "&isALifeAnnuitySale=false"
public_sale_endpoint = "&isAPublicSale=false"
order_by_endpoint = "&orderBy=postal_code"

urls = {}

for i in range(1, 2):
    url = f'{base_url}{house_apartment_endpoint}{for_sale_endpoint}{country_BE_endpoint}{life_annuity_endpoint}{public_sale_endpoint}{order_by_endpoint}&page={i}'
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    for elem in driver.find_elements(By.XPATH, "//li[@class='search-results__item']"):
        for elem_2 in elem.find_elements(By.TAG_NAME, 'a'):
            url = elem_2.get_attribute("href")
            url_key = re.findall("\d+$", str(url))
            if url_key:
                urls[url_key[0]] = url

    driver.quit()

# Open the CSV file to write data
with open("all_data.csv", 'w', newline='') as f:
    writer = csv.writer(f)

    # Write header row
    writer.writerow([
        "URL", "ID", "Price", "Location", "Type", "Subtype", "Bedrooms",
        "Land Surface", "Kitchen Type", "Fireplace Exists", "Has Terrace",
        "Terrace Surface", "Has Garden", "Garden Surface", "Net Habitable Surface",
        "Facade Count", "Has Swimming Pool", "Is Newly Built"
    ])

    # Iterate through the URLs dictionary
    for identifier, url in urls.items():
        # Use Selenium to visit the URL
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        # Extract data from the webpage using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        alldata = soup.find("div", attrs={"class": "container-main-content"}).find(
            "script", attrs={"type": "text/javascript"}).text.strip()

        data_dict = json.loads(alldata.replace('window.classified =', '').replace(';', ''))

        row = [
            url,
            data_dict["id"],
            data_dict["price"]["mainValue"],
            f"{data_dict['property']['location']['postalCode']}/{data_dict['property']['location']['locality']}",
            data_dict["property"]["type"],
            data_dict["property"]["subtype"],
            data_dict["property"]["bedroomCount"],
            data_dict["property"]["land"].get("surface", ""),
            data_dict["property"]["kitchen"].get("type", ""),
            data_dict["property"].get("fireplaceExists", ""),
            data_dict["property"].get("hasTerrace", ""),
            data_dict["property"].get("terraceSurface", ""),
            data_dict["property"].get("hasGarden", ""),
            data_dict["property"].get("gardenSurface", ""),
            data_dict["property"]["netHabitableSurface"],
            data_dict["property"]["building"].get("facadeCount", ""),
            data_dict["property"].get("hasSwimmingPool", ""),
            data_dict["flags"].get("isNewlyBuilt", "")
        ]

        # Write the row to the CSV file
        writer.writerow(row)

        driver.close()

# Print a message when finished
print("Data has been written to all_data.csv")
