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
    data_counter = 0

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
        property_dict = json.loads(property_data)

        # Extracting necessary fields from the property dictionary
        row = [
            response.url,
            property_dict.get('id', ''),
            property_dict.get('price', {}).get('mainValue', ''),
            property_dict.get('property', {}).get('location', {}).get('postalCode', '') + '/' + property_dict.get('property', {}).get('location', {}).get('locality', ''),
            property_dict.get('property', {}).get('type', ''),
            property_dict.get('property', {}).get('subtype', ''),
            property_dict.get('property', {}).get('bedroomCount', ''),
            property_dict.get('property', {}).get('land', {}).get('surface', ''),
            property_dict.get('property', {}).get('kitchen', {}).get('type', ''),
            property_dict.get('property', {}).get('fireplaceExists', ''),
            property_dict.get('property', {}).get('hasTerrace', ''),
            property_dict.get('property', {}).get('terraceSurface', ''),
            property_dict.get('property', {}).get('hasGarden', ''),
            property_dict.get('property', {}).get('gardenSurface', ''),
            property_dict.get('property', {}).get('netHabitableSurface', ''),
            property_dict.get('property', {}).get('building', {}).get('facadeCount', ''),
            property_dict.get('property', {}).get('hasSwimmingPool', ''),
            property_dict.get('flags', {}).get('isNewlyBuilt', ''),
            property_dict.get('property', {}).get('roomCount', ''),
            property_dict.get('property', {}).get('area', ''),
            property_dict.get('property', {}).get('kitchen', ''),
            property_dict.get('property', {}).get('furnished', ''),
            property_dict.get('property', {}).get('fireplace', ''),
            property_dict.get('property', {}).get('terraceArea', ''),
            property_dict.get('property', {}).get('gardenArea', ''),
            property_dict.get('property', {}).get('land', ''),
            property_dict.get('property', {}).get('building', {}).get('numberOfFacades', ''),
            property_dict.get('property', {}).get('building', {}).get('pool', ''),
            property_dict.get('property', {}).get('building', {}).get('state', '')
        ]
        
        # Append the row to the CSV file
        with open("all_data.csv", 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
            ImmospiderSpider.data_counter += 1
        
