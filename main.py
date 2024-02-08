from src.property import PropertyListing
from immoscraper.immoscraper.spiders.immospider import ImmospiderSpider
from time import perf_counter

start_time = perf_counter()

def welcome():
    '''Display the welcome message'''
    print("""
    Welcome to the Immoweb scraper!
This script will help you grab information from
the Immoweb website and save it in a CSV file.
We are starting, fasten your seatbelts!\n""")

def main():
    '''Main function'''
    welcome()
    spider = ImmospiderSpider()
    spider.start_requests()
    print(f"\n{len(ImmospiderSpider.urls)} URLs have been scraped.")
    print(f"\nTime spent to finish the task: {perf_counter() - start_time} seconds.")

    listing = PropertyListing(data_dict)
    listing.write_to_csv(writer)

print("Data has been written to all_data.csv")



if __name__ == "__main__":
    main()