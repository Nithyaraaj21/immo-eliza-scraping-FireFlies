from time import perf_counter
import re
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import threading

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def safe_get(dictionary, *keys, default=None):
    """
    Safely retrieve nested dictionary values without raising AttributeError.
    """
    for key in keys:
        if isinstance(dictionary, dict) and key in dictionary:
            dictionary = dictionary[key]
        else:
            return default
    return dictionary

# Function to scrape data from a URL
def scrape_data(url, driver):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

# Function to write data to CSV
def write_to_csv(data, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data)

# Function to handle scraping for each URL
def scrape_urls(urls, driver, filename):
    for identifier, url in urls.items():
        soup = scrape_data(url, driver)
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

# Main function
def main():
    start_time = perf_counter()

    base_url = "https://www.immoweb.be/en/search"
    house_apartment_endpoint = "/house-and-apartment"
    for_sale_endpoint = "/for-sale"
    country_BE_endpoint = "?countries=BE"
    life_annuity_endpoint = "&isALifeAnnuitySale=false"
    public_sale_endpoint = "&isAPublicSale=false"
    order_by_endpoint = "&orderBy=postal_code"

    urls = {}
    for i in range(1, 2):  # Adjust the range as needed
        url = f'{base_url}{house_apartment_endpoint}{for_sale_endpoint}{country_BE_endpoint}{life_annuity_endpoint}{public_sale_endpoint}{order_by_endpoint}&page={i}'
        driver = get_driver()
        driver.get(url)
        for elem in driver.find_elements(By.XPATH, "//li[@class='search-results__item']"):
            for elem_2 in elem.find_elements(By.TAG_NAME, 'a'):
                url = elem_2.get_attribute("href")
                url_key = re.findall("\d+$", str(url))
                if url_key:
                    urls[url_key[0]] = url
        driver.quit()

    filename = "all_data.csv"
    # Write header to CSV
    header = [
        "URL", "ID", "Price", "Location", "Type", "Subtype", "Bedrooms",
        "Land Surface", "Kitchen Type", "Fireplace Exists", "Has Terrace",
        "Terrace Surface", "Has Garden", "Garden Surface", "Net Habitable Surface",
        "Facade Count", "Has Swimming Pool", "Is Newly Built"
    ]
    write_to_csv(header, filename)

    # Create a WebDriver instance
    driver = get_driver()

    # Split URLs into chunks for threading
    chunk_size = 10
    url_chunks = [dict(list(urls.items())[i:i + chunk_size]) for i in range(0, len(urls), chunk_size)]

    threads = []
    for chunk in url_chunks:
        thread = threading.Thread(target=scrape_urls, args=(chunk, driver, filename))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Quit the WebDriver instance
    driver.quit()

    print("Data has been written to all_data.csv")
    print(f"\nTime spent to finish the task: {perf_counter() - start_time} seconds.")

# Execute the main function
if __name__ == "__main__":
    main()
