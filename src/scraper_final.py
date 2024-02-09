from time import perf_counter
import re
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_driver() -> webdriver:
    '''Creating and returning a web driver instance from Selenium'''
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized --headless=new")
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver = get_driver()

def get_data_from_url(url: str) -> BeautifulSoup:
    '''Return parsed HTML for further data processing'''
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

def safe_get(dictionary: dict, *keys, default=None) -> dict:
    '''Safely retrieve nested dictionary values without raising AttributeError'''
    for key in keys:
        if isinstance(dictionary, dict) and key in dictionary:
            dictionary = dictionary[key]
        else:
            return default
    return dictionary

def extract_urls(url: str, urls: dict, driver: webdriver) -> None:
    """Extracts URLs from a single page, using the provided driver."""
    driver.get(url)
    for elem in driver.find_elements(By.XPATH, "//li[@class='search-results__item']"):
        for link in elem.find_elements(By.TAG_NAME, 'a'):
            url = link.get_attribute("href")
            # Filter out empty URLs or those without "immoweb":
            if not url or not url.startswith("https://www.immoweb.be/"):
                continue
            url_key = re.findall("\\d+$", url)
            if url_key:
                urls[url_key[0]] = url

def scrape_urls(urls: dict, driver: webdriver, filename: str) -> dict:
    '''Function to handle scraping for each URL'''
    for identifier, url in urls.items():
        soup = get_data_from_url(url)
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
            safe_get(data_dict, "property", "land", "surface", default=""),
            safe_get(data_dict, "property", "kitchen", "type", default=""),
            safe_get(data_dict["property"], "fireplaceExists", default=""),
            safe_get(data_dict["property"], "hasTerrace", default=""),
            safe_get(data_dict["property"], "terraceSurface", default=""),
            safe_get(data_dict["property"], "hasGarden", default=""),
            safe_get(data_dict["property"], "gardenSurface", default=""),
            data_dict["property"]["netHabitableSurface"],
            safe_get(data_dict["property"]["building"], "facadeCount", default=""),
            safe_get(data_dict["property"], "hasSwimmingPool", default=""),
            safe_get(data_dict["flags"], "isNewlyBuilt", default="")
        ]
        write_to_csv(row, filename)

def write_to_csv(data, filename: str):
    '''Function to write data to CSV'''
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data)

base_url = "https://www.immoweb.be/en/search"  # Base URL for all pages
endpoints = (
    "/house-and-apartment",
    "/for-sale",
    "?countries=BE",
    "&isALifeAnnuitySale=false",
    "&isAPublicSale=false",
    "&orderBy=newest",
    )  # Combine multiple endpoints for clarity


def main():
    start_time = perf_counter()
    filename = "datatest1.csv"
    # Write header to CSV
    header = [
        "URL", "ID", "Price", "Location", "Type", "Subtype", "Bedrooms",
        "Land Surface", "Kitchen Type", "Fireplace Exists", "Has Terrace",
        "Terrace Surface", "Has Garden", "Garden Surface", "Net Habitable Surface",
        "Facade Count", "Has Swimming Pool", "Is Newly Built"
        ]
    write_to_csv(header, filename)
    for i in range(1, 2):  # Adjust the range as needed
        urls = {}
        url = f'{base_url}{''.join(endpoints)}&page={i}'
        extract_urls(url, urls, driver)
        scrape_urls(urls, driver, filename)
    print(f'This took {perf_counter() - start_time}')
    driver.quit()

if __name__ == "__main__":
    main()