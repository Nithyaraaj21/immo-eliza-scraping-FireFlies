import scrapy
from bs4 import BeautifulSoup
import csv
import json

class ImmospiderSpider(scrapy.Spider):
    name = "immospider"
    allowed_domains = ["immoweb.be"]

    urls = []

    filename = "all_data.csv"
    header = [
        "URL", "ID", "Price", "Location", "Type", "Subtype", "Bedrooms",
        "Land Surface", "Kitchen Type", "Fireplace Exists", "Has Terrace",
        "Terrace Surface", "Has Garden", "Garden Surface", "Net Habitable Surface",
        "Facade Count", "Has Swimming Pool", "Is Newly Built"
    ]

    def write_to_csv(data, filename):
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data)

    write_to_csv(header, filename)

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


    def start_requests(self):
        base_url = "https://www.immoweb.be/en/search"  # Base URL for all pages
        house_endpoints = ["/house", "/apartment"]
        for_sale_endpoint = "/for-sale"
        country_endpoint = "?countries=BE"
        life_annuity_endpoint = "&isALifeAnnuitySale=false"
        public_sale_endpoint = "&isAPublicSale=false"
        order_by_endpoints = ["&orderBy=newest", "&orderBy=relevance", "&orderBy=cheapest", "&orderBy=most_expensive", "&orderBy=postal_code"]
        
        for house_endpoint in house_endpoints:
            for order_by_endpoint in order_by_endpoints:
                for page in range(1, 3):
                    url = f'{base_url}{house_endpoint}{for_sale_endpoint}{country_endpoint}{life_annuity_endpoint}{public_sale_endpoint}{order_by_endpoint}&page={page}'
                    yield scrapy.Request(url, callback=self.parse)
        
        #print(ImmospiderSpider.urls)

    def parse(self, response):
        r_urls = response.xpath('//div[@class="card--result__body"]//a[@class="card__title-link"]/@href').getall()
        for url in r_urls:
            if url not in ImmospiderSpider.urls:
                ImmospiderSpider.urls.append(url)
                yield scrapy.Request(url, callback=self.parse_details)

            
    def parse_details(self, response):
        r_details = response.xpath('//div[@id="container-main-content"]//script[@type="text/javascript"]/text()').get()
        print(r_details)
        soup = BeautifulSoup(r_details, 'html.parser')
        all_data = soup.text.strip()
        data_dict = json.loads(all_data.replace('window.classified =', '').replace(';', ''))
        print(data_dict)
        '''row = [
            response.url,
            data_dict["id"],
            data_dict["price"]["mainValue"],
            f"{data_dict['property']['location']['postalCode']}/{data_dict['property']['location']['locality']}",
            data_dict["property"]["type"],
            data_dict["property"]["subtype"],
            data_dict["property"]["bedroomCount"],
            self.safe_get(data_dict, "property", "land", "surface", default=""),
            self.safe_get(data_dict, "property", "kitchen", "type", default=""),
            self.safe_get(data_dict["property"], "fireplaceExists", default=""),
            self.safe_get(data_dict["property"], "hasTerrace", default=""),
            self.safe_get(data_dict["property"], "terraceSurface", default=""),
            self.safe_get(data_dict["property"], "hasGarden", default=""),
            self.safe_get(data_dict["property"], "gardenSurface", default=""),
            data_dict["property"]["netHabitableSurface"],
            self.safe_get(data_dict["property"]["building"], "facadeCount", default=""),
            self.safe_get(data_dict["property"], "hasSwimmingPool", default=""),
            self.safe_get(data_dict["flags"], "isNewlyBuilt", default="")
        ]
        self.write_to_csv(row, ImmospiderSpider.filename)'''
        

        
