from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import concurrent.futures
import re
import requests
import threading
from bs4 import BeautifulSoup

base_url = "https://www.immoweb.be/en/search"  # Base URL for all pages
endpoints = (
    "/house-and-apartment",
    "/for-sale",
    "?countries=BE",
    "&isALifeAnnuitySale=false",
    "&isAPublicSale=false",
    "&orderBy=newest", # to reflect market momentum
)  # Combine multiple endpoints for clarity

def extract_urls_from_page(url, urls):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    for elem in driver.find_elements(By.XPATH, "//li[@class='search-results__item']"):
        for elem_2 in elem.find_elements(By.TAG_NAME, 'a'):
            url = elem_2.get_attribute("href")
            url_key = re.findall("\\d+$", str(url))
            if url_key:
                urls[url_key[0]] = url    
    driver.quit()

def extract_urls_from_page_chunk(urls, page_urls):
    """Extracts URLs from a chunk of pages concurrently using threads."""
    threads = []
    for url in page_urls:
        thread = threading.Thread(target=extract_urls_from_page, args=(url, urls))
        thread.start()
        threads.append(thread)

    # Wait for all threads within the chunk to finish
    for thread in threads:
        thread.join()

urls = {}
chunk_size = 10  # Adjust chunk size as needed

for i in range(0, 200, chunk_size):
    page_urls = [f"{base_url}{''.join(endpoints)}&page={page}" for page in range(i, i + chunk_size)]
    extract_urls_from_page_chunk(urls, page_urls)

print(len(urls))



# def extract_urls_from_page_chunk(urls, page_chunk):
#     """Extracts URLs from a chunk of pages."""
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = [
#             executor.submit(extract_urls_from_page, url, urls)
#             for url in page_chunk
#         ]
#         concurrent.futures.wait(futures)  # Wait for all threads to finish