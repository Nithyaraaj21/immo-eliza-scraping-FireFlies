import asyncio
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

async def extract_urls_from_page(url: str, urls: dict, driver: webdriver) -> None:
    """Extracts URLs from a single page, using the provided driver."""
    driver.get(url)
    for elem in driver.find_elements(By.XPATH, "//li[@class='search-results__item']"):
        for link in elem.find_elements(By.TAG_NAME, 'a'):
            url = link.get_attribute("href")
            url_key = re.findall("\\d+$", url)
            if url_key:
                urls[url_key[0]] = url

async def extract_urls_from_chunk(urls: dict, page_urls: list[str]):
    """Extracts URLs concurrently using asyncio."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        tasks = [asyncio.create_task(extract_urls_from_page(url, urls, driver)) for url in page_urls]
        await asyncio.gather(*tasks)
    finally:
        driver.quit()  # Ensure explicit closing even if exceptions occur

async def main():
    start_time = time.perf_counter()  # Start timer for the entire chunk
    page_urls = [f"{base_url}{''.join(endpoints)}&page={page}" for page in range(1, 200)]
    await extract_urls_from_chunk(urls, page_urls)  # Ensure you await it here
    print(urls)
    print(len(urls))
    end_time = time.perf_counter()
    print(start_time-end_time)

asyncio.run(main())  # Initiate asynchronous execution from the main thread