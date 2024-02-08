from immoscraper.immoscraper.spiders.immospider import ImmospiderSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from time import perf_counter
import csv

def main():
    '''Main function'''
    start_time = perf_counter()
    # Run the spider
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(ImmospiderSpider)
    # the script will block here until the crawling is finished
    process.start()

    # Checking consistency of the results    
    with open("immoweb_urls.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for url in ImmospiderSpider.urls:
            writer.writerow([url])
    print(f"\n{len(ImmospiderSpider.urls)} URLs have been scraped and written to immoweb_urls.csv.")
    print(f"{ImmospiderSpider.data_counter} properties have been scraped and written to all_data.csv.")
    print(f"\nTime spent to finish the scrapping: {round(perf_counter() - start_time, 2)} seconds.")

if __name__ == "__main__":
    main()