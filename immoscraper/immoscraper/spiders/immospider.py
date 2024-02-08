import scrapy


class ImmospiderSpider(scrapy.Spider):
    name = "immospider"
    allowed_domains = ["immoweb.be"]

    urls = []

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
        
        print(ImmospiderSpider.urls)

    def parse(self, response):
        r = response.xpath('//div[@class="card--result__body"]//a[@class="card__title-link"]/@href').getall()
        for url in r:
            if url not in ImmospiderSpider.urls:
                ImmospiderSpider.urls.append(url)
                yield scrapy.Request(url, callback=self.parse_details)

            

    def parse_details(self, response):
        pass
