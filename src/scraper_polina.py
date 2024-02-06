import re
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

base_url = "https://www.immoweb.be/en/search"
house_endpoint = "/house"
apartment_endpoint = "/apartment"
house_apartment_endpoint = "/house-and-apartment"
for_sale_endpoint = "/for-sale"
country_BE_endpoint = "?countries=BE"
life_annuity_endpoint = "&isALifeAnnuitySale=false"
public_sale_endpoint = "&isAPublicSale=false"
page_endpoint = "&page=1"
order_by_endpoint = "&orderBy=postal_code"

url = base_url + house_apartment_endpoint + for_sale_endpoint + country_BE_endpoint + life_annuity_endpoint + public_sale_endpoint + page_endpoint + order_by_endpoint

options_name = webdriver.ChromeOptions()
options_name.add_argument("--start-maximized")
options_name.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options_name)
driver.get(url)
ids = []
urls = {}
for elem in driver.find_elements(By.XPATH, "//li[@class='search-results__item']"):
    for elem_2 in elem.find_elements(By.TAG_NAME, 'a'):
        url = elem_2.get_attribute("href")
        url_key = re.findall("\d+$", str(url))
        if url_key:
            urls[url_key[0]] = url

print(urls)