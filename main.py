from immoscraper.immoscraper.spiders.immospider import ImmospiderSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from time import perf_counter
import csv

def main():
    # Instantiate a CrawlerProcess
    process = CrawlerProcess(get_project_settings())

    # Add spider to the process
    process.crawl(ImmospiderSpider)  

    # Start the crawling process
    process.start()

    print(f"\n{len(ImmospiderSpider.urls)} URLs have been scraped and written to immoweb_urls.csv.")
    print(f"{ImmospiderSpider.data_counter} properties have been scraped and written to all_data.csv.")
    print(f"\nTime spent to finish the scrapping: {round(perf_counter() - start_time, 2)} seconds.")

if __name__ == "__main__":
    main()

