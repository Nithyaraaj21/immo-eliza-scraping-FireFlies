from time import perf_counter
start_time = perf_counter()

import scrapy
from bs4 import BeautifulSoup
import json
import pandas as pd
import os

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
        #public_sale_endpoint = "&isAPublicSale=false"
        order_by_endpoints = ["&orderBy=newest", "&orderBy=relevance", "&orderBy=cheapest", "&orderBy=most_expensive", "&orderBy=postal_code"]
        
        # Loop through all the combinations of endpoints to get all possible pages of the website
        for house_endpoint in house_endpoints:
            for order_by_endpoint in order_by_endpoints:
                for page in range(1, 334):
                    # Construct the URL to send the request to
                    url = f'{base_url}{house_endpoint}{for_sale_endpoint}{country_endpoint}{life_annuity_endpoint}{order_by_endpoint}&page={page}'
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
            heating_type =  property_dict.get('property', {}).get('energy', {}).get('heatingType')
            Double_glazing =  convert_value(property_dict.get('property', {}).get('energy', {}).get('hasDoubleGlazing'))
            energy_consumption_level = property_dict.get('transaction').get('certificates', {}).get('primaryEnergyConsumptionPerSqm')
            EPC_score= property_dict.get('transaction').get('certificates', {}).get('epcScore')
            Cadastral_income = property_dict.get('transaction').get('sale', {}).get('cadastralIncome')
            #has_office_space = property_dict.get('specificities', {}).get('SME', {}).get('office', {}).get('exists')
            indoor_parking_spaces = property_dict.get('property', {}).get('parkingCountIndoor')
            outdoor_parking_spaces = property_dict.get('property', {}).get('parkingCountOutdoor')
            closed_box_parking_spaces = property_dict.get('property', {}).get('parkingCountClosedBox')
        except AttributeError as e:
            print(f'Error extracting property details: {e}')
            construction_year = None
            condition = None
            land_surface = None
            kitchen_type = None
            facadeCount = None
            heating_type = None
            energy_consumption_level = None
            #has_office_space = None
            indoor_parking_spaces = None
            outdoor_parking_spaces = None
            closed_box_parking_spaces = None
            EPC_score = None
            Double_glazing= None
            Cadastral_income = None

        
        sale_type = None
        flags = property_dict.get('flags', {})
        if flags.get('isPublicSale'):
            sale_type = 'Public Sale'
        elif flags.get('isNotarySale'):
            sale_type = 'Notary Sale'
        elif flags.get('isAnInteractiveSale'):
            sale_type = 'Interactive Sale'
        
        # Creating a DataFrame with the extracted data
        data = {
            #'URL': [response.url],
            'ID': [property_dict.get('id', '')],
            'Price': [property_dict.get('price', {}).get('mainValue', '')],
            'region': [property_dict.get('property', {}).get('location', {}).get('region', '')],
            'provience': [property_dict.get('property', {}).get('location', {}).get('province', '')],
            'District': [property_dict.get('property', {}).get('location', {}).get('district', '')],
            'Postal_Code': [property_dict.get('property', {}).get('location', {}).get('postalCode', '')],
            'Locality': [property_dict.get('property', {}).get('location', {}).get('locality', '')],
            'Latitude': [property_dict.get('property', {}).get('location', {}).get('latitude', '')],
            'Longitude': [property_dict.get('property', {}).get('location', {}).get('longitude', '')],
            'Construction_Year': [construction_year],
            'Condition': [condition],
            'Type': [property_dict.get('property', {}).get('type', '')],
            'Subtype': [property_dict.get('property', {}).get('subtype', '')],
            'Bedroom_Count': [property_dict.get('property', {}).get('bedroomCount', '')],
            'Land_Surface': [land_surface],
            'Kitchen_Type': [kitchen_type],
            'Sale_Type': [sale_type],
            'Furnished': [convert_value(property_dict.get('transaction').get('sale',{}).get('isFurnished'))],
            'Fireplace_Exists': [convert_value(property_dict.get('property', {}).get('fireplaceExists'))],
            'Has_Terrace': [convert_value(property_dict.get('property', {}).get('hasTerrace'))],
            'Terrace_Surface': [convert_value(property_dict.get('property', {}).get('terraceSurface'))],
            'Has_Garden': [convert_value(property_dict.get('property', {}).get('hasGarden'))],
            'Garden_Surface': [convert_value(property_dict.get('property', {}).get('gardenSurface'))],
            'Habitable_Surface': [convert_value(property_dict.get('property', {}).get('netHabitableSurface'))],
            'Facade_Count': [facadeCount],
            'Swimming_Pool': [convert_value(property_dict.get('property', {}).get('hasSwimmingPool'))],
            #'Has Swimming Pool': [property_dict.get('property', {}).get('wellnessEquipment', {}).get('hasSwimmingPool')],
            'Indoor_Parking': [indoor_parking_spaces],
            'Outdoor_Parking': [outdoor_parking_spaces],
            #'Closed_Box_Parking': [closed_box_parking_spaces],
            'Heating_Type': [heating_type],
            'Energy_Consumption_Level': [energy_consumption_level],
            'EPC':[EPC_score],
            'Double_glazing':[Double_glazing],
            #'Has Office Space': [has_office_space],
            'Cadastral_income': [Cadastral_income]
        }
        
        df = pd.DataFrame(data)
            # Append the DataFrame to the CSV file
        if not os.path.isfile("immoweb_raw_vf.csv"):
                df.to_csv("immoweb_raw_vf.csv", mode='a', index=False, header=True)
        else:
                df.to_csv("immoweb_raw_vf.csv", mode='a', index=False, header=False)
    print(f"\nTime spent to finish the task: {perf_counter() - start_time} seconds.")
