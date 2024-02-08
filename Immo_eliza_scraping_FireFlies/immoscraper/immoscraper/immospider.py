import scrapy
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd

class ImmospiderSpider(scrapy.Spider):
    '''This spider scrapes immoweb.be for real estate data.'''
    name = "immospider"
    allowed_domains = ["immoweb.be"]

    urls=[]

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
        print(f'Number of urls: {len(ImmospiderSpider.urls)}')
        
    def parse(self, response):
        '''Function to parse the response and extract the URLs of the properties.'''
        r_urls = response.xpath('//div[@class="card--result__body"]//a[@class="card__title-link"]/@href').getall()
        for url in r_urls:
            ImmospiderSpider.urls.append(url)
            # Send a request to the individual property URL and call the parse_details function
            yield scrapy.Request(url, callback=self.parse_details)

            
    def parse_details(self, response):
        '''Function to parse the details of the individual property, convert them and append to the CSV file.'''
        r_details = response.xpath('//div[@id="container-main-content"]//script[@type="text/javascript"]/text()').get()
        #print(r_details)
        soup = BeautifulSoup(r_details, 'html.parser')
        property_data = soup.text.strip().replace('window.classified = ', '').replace(';', '')
        property_dict = json.loads(property_data)
        
        # Convert True/False to 1/0 and replace None with 'none'
        def convert_value(value):
            if value is True:
                return 1
            elif value is False:
                return 0
            elif value is None:
                return None
            else:
                return value
        
        # Extracting necessary fields from the property dictionary
        try:
            construction_year = property_dict.get('property', {}).get('building', {}).get('constructionYear')
            condition = property_dict.get('property', {}).get('building', {}).get('condition')
            land_surface = property_dict.get('property', {}).get('land', {}).get('surface')
            kitchen_type = property_dict.get('property', {}).get('kitchen', {}).get('type')
            facadeCount = property_dict.get('property', {}).get('building', {}).get('facadeCount')
        except AttributeError as e:
            print(f'Error extracting property details: {e}')
            construction_year = None
            condition = None
            land_surface = None
            kitchen_type = None
            facadeCount = None

        
        sale_type = None
        flags = property_dict.get('flags', {})
        if flags.get('isPublicSale'):
            sale_type = 'Public Sale'
        elif flags.get('isNotarySale'):
            sale_type = 'Notary Sale'
        elif flags.get('isAnInteractiveSale'):
            sale_type = 'Interactive Sale'
        row = [
            response.url,
            property_dict.get('id', ''),
            property_dict.get('price', {}).get('mainValue', ''),
            property_dict.get('property', {}).get('location', {}).get('postalCode', ''),
            property_dict.get('property', {}).get('location', {}).get('locality', ''),
            construction_year,
            condition,
            property_dict.get('property', {}).get('type', ''),
            property_dict.get('property', {}).get('subtype', ''),
            property_dict.get('property', {}).get('bedroomCount', ''),
            land_surface,
            kitchen_type,
            sale_type,
            convert_value(property_dict.get('property', {}).get('fireplaceExists')),
            convert_value(property_dict.get('property', {}).get('hasTerrace')),
            convert_value(property_dict.get('property', {}).get('terraceSurface')),
            convert_value(property_dict.get('property', {}).get('hasGarden')),
            convert_value(property_dict.get('property', {}).get('gardenSurface')),
            convert_value(property_dict.get('property', {}).get('netHabitableSurface')),
            facadeCount,
            convert_value(property_dict.get('property', {}).get('hasSwimmingPool')),
            #convert_value(property_dict.get('property', {}).get('building', {}).get('condition')),
        ]
        
        # Append the row to the CSV file
        with open("all_data.csv", 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
