import scrapy
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd

class ImmospiderSpider(scrapy.Spider):
    '''This spider scrapes immoweb.be for real estate data.'''
    name = "immospider"
    allowed_domains = ["immoweb.be"]

    # List to store all URLs of the propeties to prevent duplicates
    urls = []
    # Dictionary to store the data of each property
    data_dict = {}
    #df = pd.DataFrame()

    with open("all_data.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            fieldnames = [
                "URL", "ID", "Type of Sale", "Year of Construction", "Price", "Location", "Type", "Subtype", "Bedrooms",
                "Land Surface", "Kitchen Type", "Fireplace Exists", "Has Terrace",
                "Terrace Surface", "Has Garden", "Garden Surface", "Net Habitable Surface",
                "Facade Count", "Has Swimming Pool", "Is Newly Built",
                "Number of Rooms", "Area", "Kitchen", "Furnished", "Fireplace",
                "Terrace Area", "Garden Area", "Land", "Number of Facades", "Pool", "State"
            ]
            writer.writerow(fieldnames)

    def start_requests(self):
        '''Function to start the scraping process.'''
        base_url = "https://www.immoweb.be/en/search"  # Base URL for all pages
        house_endpoints = ["/house", "/apartment"]
        for_sale_endpoint = "/for-sale"
        country_endpoint = "?countries=BE"
        life_annuity_endpoint = "&isALifeAnnuitySale=false"
        public_sale_endpoint = "&isAPublicSale=false"
        order_by_endpoints = ["&orderBy=newest", "&orderBy=relevance", "&orderBy=cheapest", "&orderBy=most_expensive", "&orderBy=postal_code"]
        
        # Loop through all the combinations of endpoints to get all possible pages of the website
        for house_endpoint in house_endpoints:
            for order_by_endpoint in order_by_endpoints:
                for page in range(1, 2):
                    # Construct the URL to send the request to
                    url = f'{base_url}{house_endpoint}{for_sale_endpoint}{country_endpoint}{life_annuity_endpoint}{public_sale_endpoint}{order_by_endpoint}&page={page}'
                    # Send a request to the URL and call the parse function
                    yield scrapy.Request(url, callback=self.parse)
        
        # print(ImmospiderSpider.urls, len(ImmospiderSpider.urls))
        #print(ImmospiderSpider.pd)

    def parse(self, response):
        '''Function to parse the response and extract the URLs of the properties.'''
        r_urls = response.xpath('//div[@class="card--result__body"]//a[@class="card__title-link"]/@href').getall()
        for url in r_urls:
            if url not in ImmospiderSpider.urls:
                # Append the URL to the list of URLs
                ImmospiderSpider.urls.append(url)
                # Send a request to the individual property URL and call the parse_details function
                yield scrapy.Request(url, callback=self.parse_details)

            
    def parse_details(self, response):
        '''Function to parse the details of the individual property, convert them and write a line to a CSV file.'''
        r_details = response.xpath('//div[@id="container-main-content"]//script[@type="text/javascript"]/text()').get()
        #print(r_details)
        soup = BeautifulSoup(r_details, 'html.parser')
        property_data = soup.text.strip().replace('window.classified = ', '').replace(';', '')
        property_dict : dict = json.loads(property_data)
        df = pd.DataFrame.from_dict(property_dict, orient='index')
        df.to_csv('out.csv', index=False)
        # Create a PropertyListing object
        #listing = PropertyListing(property_dict)
        
