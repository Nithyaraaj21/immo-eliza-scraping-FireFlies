from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup

'''We are requesting data pages to retrieve each property URL'''
root_url = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&isAPublicSale=false&isALifeAnnuitySale=false&orderBy=relevance'

service = Service(executable_path='./src/chromedriver.exe') # To execute drivers for Chrome v114
options = webdriver.ChromeOptions()

options.add_experimental_option("detach", True) # To detach the execution of the browser from the code

driver=webdriver.Chrome(service=service, options=options) 
driver.get(root_url)


'''We are clicking the cookie'''

cookie_button = driver.find_element(By.XPATH, "//button[@data-testid='uc-accept-all-button']")
cookie_button.click()


