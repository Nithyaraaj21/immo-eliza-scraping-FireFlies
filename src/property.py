import re
import json
import csv

class PropertyListing:
    def __init__(self, data_dict):
        self.data_dict = data_dict
    
    def extract_attributes(self):
        attributes = {
            "Type of Sale": self.type_sale(),
            "Year of Construction": self.construction_year(),
            "Type": self.type_property(),
            "Location": self.locality(),
            "Subtype": self.safe_get('property', 'subtype'),
            "Price": self.price(),
            "Bedrooms": self.safe_get('property', 'bedroomCount'),
            "Land Surface": self.land(),
            "Kitchen Type": self.kitchen(),
            "Fireplace Exists": self.fire(),
            "Has Terrace": self.terrace_area(),
            "Terrace Surface": self.terrace_area(),
            "Has Garden": self.garden_area(),
            "Garden Surface": self.garden_area(),
            "Net Habitable Surface": self.area(),
            "Facade Count": self.safe_get('property', 'building', 'facadeCount'),
            "Has Swimming Pool": self.pool(),
            "Is Newly Built": self.state(),
            "Number of Rooms": self.safe_get('property', 'bedroomCount'),
            "Area": self.area(),
            "Kitchen": self.kitchen(),
            "Furnished": self.furnished(),
            "Fireplace": self.fire(),
            "Terrace Area": self.terrace_area(),
            "Garden Area": self.garden_area(),
            "Land": self.land(),
            "Number of Facades": self.safe_get('property', 'building', 'facadeCount'),
            "Pool": self.pool(),
            "State": self.state()
        }
        return attributes

    def safe_get(self, *keys, default=None):
        '''Safely retrieve nested dictionary values without raising AttributeError.'''
        dictionary = self.data_dict
        for key in keys:
            if isinstance(dictionary, dict) and key in dictionary:
                dictionary = dictionary[key]
            else:
                return default
        return dictionary

    def type_sale(self):
        try:
            if self.data_dict['flags']['isPublicSale']:
                return 'Public Sale'
            elif self.data_dict['flags']['isNotarySale']:
                return 'Notary Sale'
            elif self.data_dict['flags']['isAnInteractiveSale']:
                return 'Interactive Sale'
            else:
                return None
        except:
            return None
    
    def construction_year(self):
        try:
            return self.data_dict['property']['constructionYear']
        except:
            return None
    
    def type_property(self):
        try:
            return self.data_dict['property']['type']
        except:
            return None

    def locality(self):
        return self.safe_get('property', 'location', 'postalCode')

    def price(self):
        transaction = self.safe_get('transaction', 'sale')
        if transaction:
            return transaction.get('price')
        return None

    def kitchen(self):
        kitchen_type = self.safe_get('property', 'kitchen', 'type')
        return 1 if kitchen_type else 0

    def furnished(self):
        return 1 if self.safe_get('transaction', 'sale', 'isFurnished') else 0

    def fire(self):
        return 1 if self.safe_get('property', 'fireplaceExists') else 0

    def terrace_area(self):
        if self.safe_get('property', 'hasTerrace'):
            return self.safe_get('property', 'terraceSurface')
        return 0

    def garden_area(self):
        if self.safe_get('property', 'hasGarden'):
            return self.safe_get('property', 'gardenSurface')
        return 0

    def land(self):
        land_info = self.safe_get('property', 'land')
        return land_info.get('surface') if land_info else 0

    def pool(self):
        soup = self.get_soup()
        swim_regex = re.findall('swimming pool', str(soup))
        return 1 if swim_regex else 0

    def state(self):
        return self.safe_get('property', 'building', 'condition')

    def area(self):
        return self.safe_get('property', 'netHabitableSurface')

    def num_rooms(self):
        return self.safe_get('property', 'bedroomCount')

    def num_facade(self):
        return self.safe_get('property', 'building', 'facadeCount')
