import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import re

base_url = "https://www.immoweb.be/en/search"  # Base URL for all pages
endpoints = (
    "/house-and-apartment",
    "/for-sale",
    "?countries=BE",
    "&isALifeAnnuitySale=false",
    "&isAPublicSale=false",
    "&orderBy=newest",
)  # Combine multiple endpoints for clarity

urls = {} # initiate the dict of urls
chunk_size = 40  # Adjust the size of pages to be checked per request

def extract_urls_from_page(url, urls, driver):
    """Extracts URLs from a single page, using the provided driver."""
    driver.get(url)
    for elem in driver.find_elements(By.XPATH, "//li[@class='search-results__item']"):
        for link in elem.find_elements(By.TAG_NAME, 'a'):
            url = link.get_attribute("href")
            url_key = re.findall("\\d+$", url)
            if url_key:
                urls[url_key[0]] = url

def extract_urls_from_chunk(urls, page_urls):
    """Extracts URLs from a chunk of pages concurrently using threads."""
    start_time = time.perf_counter()  # Start timer for the entire chunk
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver: # driver creation inside function to ensure proper closing & avoid resource leaks
        threads = []
        for url in page_urls:
            thread = threading.Thread(target=extract_urls_from_page, args=(url, urls, driver))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
    driver.quit()
    end_time = time.perf_counter()
    print(f"Extracted URLs from {len(page_urls)} pages in {end_time - start_time:.2f} seconds (total)")  # Print performance for the whole chunk
    
for i in range(1, 333, chunk_size):
    page_urls = [f"{base_url}{''.join(endpoints)}&page={page}" for page in range(i, i + chunk_size)]
    extract_urls_from_chunk(urls, page_urls)

print(urls)