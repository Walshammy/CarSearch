import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime
import warnings
import json
import os

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class CarAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Comprehensive fuel efficiency data (L/100km) for multiple brands
        self.fuel_efficiency = {
            # Subaru
            'subaru': {
                'impreza': {'2008-2012': 8.5, '2012-2016': 7.8, '2017+': 7.2},
                'xv': {'2012-2016': 8.2, '2017+': 7.5},
                'crosstrek': {'2012-2016': 8.2, '2017+': 7.5},
                'forester': {'2008-2012': 9.8, '2013-2018': 8.9, '2019+': 8.4},
                'outback': {'2009-2014': 10.2, '2015-2019': 8.7, '2020+': 8.1},
                'legacy': {'2009-2014': 9.8, '2015-2019': 8.9, '2020+': 8.3},
                'brz': {'2012+': 8.8},
                'wrx': {'2008-2014': 11.5, '2015+': 10.2},
                'sti': {'all': 13.0}
            },
            # Toyota
            'toyota': {
                'corolla': {'2008-2012': 7.8, '2013-2018': 7.2, '2019+': 6.8},
                'camry': {'2008-2012': 9.2, '2013-2018': 8.5, '2019+': 8.1},
                'rav4': {'2008-2012': 9.8, '2013-2018': 8.9, '2019+': 8.2},
                'prius': {'2008-2012': 4.5, '2013-2018': 4.2, '2019+': 4.0},
                'yaris': {'2008-2012': 6.8, '2013-2018': 6.2, '2019+': 5.9},
                'hilux': {'2008-2012': 11.5, '2013-2018': 10.8, '2019+': 10.2},
                'prado': {'2008-2012': 12.8, '2013-2018': 11.9, '2019+': 11.2},
                'aurion': {'2008-2012': 10.5, '2013-2018': 9.8, '2019+': 9.2}
            },
            # Honda
            'honda': {
                'civic': {'2008-2012': 7.5, '2013-2018': 7.0, '2019+': 6.8},
                'accord': {'2008-2012': 9.0, '2013-2018': 8.5, '2019+': 8.0},
                'cr-v': {'2008-2012': 9.5, '2013-2018': 8.8, '2019+': 8.2},
                'fit': {'2008-2012': 6.5, '2013-2018': 6.0, '2019+': 5.8},
                'jazz': {'2008-2012': 6.5, '2013-2018': 6.0, '2019+': 5.8},
                'pilot': {'2008-2012': 11.8, '2013-2018': 11.0, '2019+': 10.5},
                'odyssey': {'2008-2012': 10.5, '2013-2018': 9.8, '2019+': 9.2}
            },
            # Mazda
            'mazda': {
                'mazda3': {'2008-2012': 8.2, '2013-2018': 7.5, '2019+': 7.0},
                'mazda6': {'2008-2012': 9.5, '2013-2018': 8.8, '2019+': 8.2},
                'cx-5': {'2012-2016': 8.5, '2017+': 7.8},
                'cx-3': {'2015+': 7.2},
                'cx-9': {'2008-2012': 12.5, '2013-2018': 11.8, '2019+': 11.0},
                'mx-5': {'2008-2012': 8.8, '2013-2018': 8.2, '2019+': 7.8},
                'bt-50': {'2008-2012': 11.8, '2013-2018': 11.0, '2019+': 10.5}
            },
            # Ford
            'ford': {
                'focus': {'2008-2012': 8.5, '2013-2018': 7.8, '2019+': 7.2},
                'falcon': {'2008-2012': 11.5, '2013-2016': 10.8},
                'territory': {'2008-2012': 12.8, '2013-2016': 12.0},
                'ranger': {'2008-2012': 12.5, '2013-2018': 11.8, '2019+': 11.2},
                'everest': {'2015+': 11.5},
                'ecosport': {'2013+': 8.2},
                'kuga': {'2008-2012': 9.8, '2013-2018': 9.2, '2019+': 8.8}
            },
            # Nissan
            'nissan': {
                'pulsar': {'2008-2012': 8.0, '2013-2018': 7.5, '2019+': 7.0},
                'altima': {'2008-2012': 9.5, '2013-2018': 8.8, '2019+': 8.2},
                'x-trail': {'2008-2012': 10.2, '2013-2018': 9.5, '2019+': 8.8},
                'qashqai': {'2008-2012': 9.8, '2013-2018': 9.0, '2019+': 8.5},
                'navara': {'2008-2012': 12.0, '2013-2018': 11.2, '2019+': 10.8},
                'patrol': {'2008-2012': 15.5, '2013-2018': 14.8, '2019+': 14.0},
                'juke': {'2011+': 8.5}
            },
            # Hyundai
            'hyundai': {
                'i30': {'2008-2012': 8.0, '2013-2018': 7.5, '2019+': 7.0},
                'elantra': {'2008-2012': 8.5, '2013-2018': 7.8, '2019+': 7.2},
                'tucson': {'2008-2012': 9.8, '2013-2018': 9.0, '2019+': 8.5},
                'santa_fe': {'2008-2012': 11.2, '2013-2018': 10.5, '2019+': 9.8},
                'i20': {'2008-2012': 7.2, '2013-2018': 6.8, '2019+': 6.5},
                'accent': {'2008-2012': 7.8, '2013-2018': 7.2, '2019+': 6.8},
                'getz': {'2008-2012': 7.5, '2013-2018': 7.0, '2019+': 6.8}
            },
            # Mitsubishi
            'mitsubishi': {
                'lancer': {'2008-2012': 8.2, '2013-2018': 7.5, '2019+': 7.0},
                'outlander': {'2008-2012': 10.5, '2013-2018': 9.8, '2019+': 9.2},
                'asx': {'2010+': 8.8},
                'triton': {'2008-2012': 11.8, '2013-2018': 11.0, '2019+': 10.5},
                'pajero': {'2008-2012': 13.5, '2013-2018': 12.8, '2019+': 12.0},
                'mirage': {'2012+': 6.8},
                'eclipse_cross': {'2017+': 8.5}
            },
            # Volkswagen
            'volkswagen': {
                'golf': {'2008-2012': 7.8, '2013-2018': 7.2, '2019+': 6.8},
                'passat': {'2008-2012': 9.2, '2013-2018': 8.5, '2019+': 8.0},
                'tiguan': {'2008-2012': 9.8, '2013-2018': 9.0, '2019+': 8.5},
                'polo': {'2008-2012': 7.2, '2013-2018': 6.8, '2019+': 6.5},
                'jetta': {'2008-2012': 8.5, '2013-2018': 7.8, '2019+': 7.2},
                'touareg': {'2008-2012': 12.5, '2013-2018': 11.8, '2019+': 11.0}
            },
            # BMW
            'bmw': {
                '3_series': {'2008-2012': 8.8, '2013-2018': 8.2, '2019+': 7.8},
                '5_series': {'2008-2012': 10.2, '2013-2018': 9.5, '2019+': 9.0},
                'x3': {'2008-2012': 10.8, '2013-2018': 10.0, '2019+': 9.5},
                'x5': {'2008-2012': 12.5, '2013-2018': 11.8, '2019+': 11.2},
                '1_series': {'2008-2012': 8.5, '2013-2018': 7.8, '2019+': 7.5}
            },
            # Audi
            'audi': {
                'a3': {'2008-2012': 8.2, '2013-2018': 7.5, '2019+': 7.0},
                'a4': {'2008-2012': 9.5, '2013-2018': 8.8, '2019+': 8.2},
                'a6': {'2008-2012': 10.8, '2013-2018': 10.0, '2019+': 9.5},
                'q5': {'2008-2012': 10.5, '2013-2018': 9.8, '2019+': 9.2},
                'q7': {'2008-2012': 12.8, '2013-2018': 12.0, '2019+': 11.5}
            }
        }
        
        # Popular car brands to search for
        self.brands = [
            'subaru', 'toyota', 'honda', 'mazda', 'ford', 'nissan', 
            'hyundai', 'mitsubishi', 'volkswagen', 'bmw', 'audi'
        ]
        
        self.base_url = "https://www.trademe.co.nz/a/motors/cars"
        self.listings = []
        self.dataset_file = "car_dataset.csv"

    def get_fuel_efficiency(self, brand, model, year):
        """Get fuel efficiency for a specific brand, model and year"""
        brand_lower = brand.lower()
        model_lower = model.lower()
        
        if brand_lower not in self.fuel_efficiency:
            return None
            
        brand_data = self.fuel_efficiency[brand_lower]
        
        # Find matching model
        model_key = None
        for key in brand_data.keys():
            if key in model_lower or model_lower in key:
                model_key = key
                break
                
        if not model_key:
            return None
            
        efficiency_data = brand_data[model_key]
        
        # Determine year range
        if year >= 2020:
            return efficiency_data.get('2020+') or efficiency_data.get('2019+') or efficiency_data.get('2017+')
        elif year >= 2019:
            return efficiency_data.get('2019+') or efficiency_data.get('2017+') or efficiency_data.get('2015-2019')
        elif year >= 2017:
            return efficiency_data.get('2017+') or efficiency_data.get('2015-2019')
        elif year >= 2015:
            return efficiency_data.get('2015-2019') or efficiency_data.get('2013-2018')
        elif year >= 2013:
            return efficiency_data.get('2013-2018') or efficiency_data.get('2012-2016')
        elif year >= 2012:
            return efficiency_data.get('2012-2016') or efficiency_data.get('2012+') or efficiency_data.get('2008-2012')
        elif year >= 2008:
            return efficiency_data.get('2008-2012') or efficiency_data.get('2009-2014')
        else:
            return efficiency_data.get('all', 11.0)

    def scrape_brand_listings(self, brand, max_price=12500, min_price=7500, max_pages=3):
        """Scrape listings for a specific brand"""
        print(f"Scraping {brand.title()} listings...")
        
        brand_listings = []
        url = f"{self.base_url}/{brand}"
        
        for page in range(1, max_pages + 1):
            print(f"  Page {page}...")
            
            params = {
                'price_min': min_price,
                'price_max': max_price,
                'page': page
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find listing containers
                listings = soup.find_all('div', class_='listing-item') or soup.find_all('article')
                
                if not listings:
                    print(f"  No listings found on page {page}")
                    break
                
                for listing in listings:
                    try:
                        listing_data = self.extract_listing_data(listing, brand)
                        if listing_data:
                            brand_listings.append(listing_data)
                    except Exception as e:
                        print(f"  Error extracting listing: {e}")
                        continue
                
                # Be respectful with scraping
                time.sleep(2)
                
            except Exception as e:
                print(f"  Error scraping page {page}: {e}")
                continue
        
        print(f"  Found {len(brand_listings)} {brand.title()} listings")
        return brand_listings

    def extract_listing_data(self, listing, brand):
        """Extract data from a single listing"""
        try:
            # Extract title
            title_elem = listing.find('h3') or listing.find('a', class_='listing-title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract price
            price_elem = listing.find(class_=re.compile('price|amount'))
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price = self.extract_price(price_text)
            
            # Extract year and model from title
            year, model = self.extract_year_model(title, brand)
            
            # Look for mileage/odometer
            mileage_elem = listing.find(text=re.compile(r'\d+,?\d*\s*km'))
            mileage = self.extract_mileage(mileage_elem) if mileage_elem else None
            
            # Extract location if available
            location_elem = listing.find(class_=re.compile('location|region'))
            location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            return {
                'title': title,
                'brand': brand.title(),
                'year': year,
                'model': model,
                'price': price,
                'mileage': mileage,
                'location': location,
                'scraped_date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            print(f"Error extracting listing data: {e}")
            return None

    def extract_price(self, price_text):
        """Extract numeric price from price text"""
        numbers = re.findall(r'[\d,]+', price_text.replace('$', ''))
        if numbers:
            return int(numbers[0].replace(',', ''))
        return 0

    def extract_year_model(self, title, brand):
        """Extract year and model from title"""
        # Look for year (4 digits)
        year_match = re.search(r'(19|20)\d{2}', title)
        year = int(year_match.group()) if year_match else None
        
        # Extract model from title (remove brand name and year)
        title_lower = title.lower()
        brand_lower = brand.lower()
        
        # Remove brand name and year from title to get model
        model_text = title_lower.replace(brand_lower, '').strip()
        year_pattern = r'\b(19|20)\d{2}\b'
        model_text = re.sub(year_pattern, '', model_text).strip()
        
        # Clean up model name
        model_text = re.sub(r'[^\w\s]', ' ', model_text)
        model_text = ' '.join(model_text.split())
        
        model = model_text.title() if model_text else 'Unknown'
        
        return year, model

    def extract_mileage(self, mileage_text):
        """Extract numeric mileage from text"""
        if isinstance(mileage_text, str):
            numbers = re.findall(r'[\d,]+', mileage_text)
            if numbers:
                return int(numbers[0].replace(',', ''))
        return None

    def create_sample_data(self):
        """Create comprehensive sample data for testing"""
        print("Creating sample dataset...")
        
        sample_data = []
        
        # Subaru samples
        subaru_samples = [
            {'title': '2014 Subaru XV 2.0i', 'brand': 'Subaru', 'year': 2014, 'model': 'XV', 'price': 11500, 'mileage': 145000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2013 Subaru Impreza XV', 'brand': 'Subaru', 'year': 2013, 'model': 'Impreza XV', 'price': 10200, 'mileage': 165000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Subaru Forester 2.5X', 'brand': 'Subaru', 'year': 2012, 'model': 'Forester', 'price': 9800, 'mileage': 175000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Subaru Impreza 2.0i', 'brand': 'Subaru', 'year': 2015, 'model': 'Impreza', 'price': 12000, 'mileage': 125000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
            {'title': '2011 Subaru Outback 2.5i', 'brand': 'Subaru', 'year': 2011, 'model': 'Outback', 'price': 8900, 'mileage': 185000, 'location': 'Tauranga', 'scraped_date': '2025-09-15'},
        ]
        
        # Toyota samples
        toyota_samples = [
            {'title': '2013 Toyota Corolla Ascent', 'brand': 'Toyota', 'year': 2013, 'model': 'Corolla', 'price': 9500, 'mileage': 155000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Toyota Camry Altise', 'brand': 'Toyota', 'year': 2014, 'model': 'Camry', 'price': 11200, 'mileage': 135000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Toyota RAV4 GX', 'brand': 'Toyota', 'year': 2012, 'model': 'RAV4', 'price': 10800, 'mileage': 165000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Toyota Prius C', 'brand': 'Toyota', 'year': 2015, 'model': 'Prius', 'price': 12500, 'mileage': 115000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
            {'title': '2011 Toyota Yaris YR', 'brand': 'Toyota', 'year': 2011, 'model': 'Yaris', 'price': 7500, 'mileage': 195000, 'location': 'Tauranga', 'scraped_date': '2025-09-15'},
        ]
        
        # Honda samples
        honda_samples = [
            {'title': '2013 Honda Civic VTi', 'brand': 'Honda', 'year': 2013, 'model': 'Civic', 'price': 9200, 'mileage': 145000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Honda Accord Euro', 'brand': 'Honda', 'year': 2014, 'model': 'Accord', 'price': 11800, 'mileage': 125000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Honda CR-V Sport', 'brand': 'Honda', 'year': 2012, 'model': 'CR-V', 'price': 10500, 'mileage': 175000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Honda Fit Jazz', 'brand': 'Honda', 'year': 2015, 'model': 'Fit', 'price': 9800, 'mileage': 135000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
        ]
        
        # Mazda samples
        mazda_samples = [
            {'title': '2013 Mazda Mazda3 Maxx', 'brand': 'Mazda', 'year': 2013, 'model': 'Mazda3', 'price': 8800, 'mileage': 155000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Mazda Mazda6 Touring', 'brand': 'Mazda', 'year': 2014, 'model': 'Mazda6', 'price': 11200, 'mileage': 135000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Mazda CX-5 Maxx Sport', 'brand': 'Mazda', 'year': 2012, 'model': 'CX-5', 'price': 10800, 'mileage': 165000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Mazda CX-3 Maxx', 'brand': 'Mazda', 'year': 2015, 'model': 'CX-3', 'price': 12200, 'mileage': 115000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
        ]
        
        # Ford samples
        ford_samples = [
            {'title': '2013 Ford Focus Trend', 'brand': 'Ford', 'year': 2013, 'model': 'Focus', 'price': 8500, 'mileage': 165000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Ford Falcon XR6', 'brand': 'Ford', 'year': 2014, 'model': 'Falcon', 'price': 11500, 'mileage': 145000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Ford Territory TX', 'brand': 'Ford', 'year': 2012, 'model': 'Territory', 'price': 9800, 'mileage': 185000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Ford Ranger XLT', 'brand': 'Ford', 'year': 2015, 'model': 'Ranger', 'price': 12500, 'mileage': 125000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
        ]
        
        # Add more samples for comprehensive dataset
        # Nissan samples
        nissan_samples = [
            {'title': '2013 Nissan Pulsar ST', 'brand': 'Nissan', 'year': 2013, 'model': 'Pulsar', 'price': 9200, 'mileage': 145000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Nissan Altima SV', 'brand': 'Nissan', 'year': 2014, 'model': 'Altima', 'price': 11200, 'mileage': 135000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Nissan X-Trail ST', 'brand': 'Nissan', 'year': 2012, 'model': 'X-Trail', 'price': 10800, 'mileage': 165000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Nissan Qashqai ST', 'brand': 'Nissan', 'year': 2015, 'model': 'Qashqai', 'price': 12200, 'mileage': 115000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
        ]
        
        # Hyundai samples
        hyundai_samples = [
            {'title': '2013 Hyundai i30 Active', 'brand': 'Hyundai', 'year': 2013, 'model': 'i30', 'price': 8800, 'mileage': 155000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Hyundai Elantra Elite', 'brand': 'Hyundai', 'year': 2014, 'model': 'Elantra', 'price': 10200, 'mileage': 135000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Hyundai Tucson Active', 'brand': 'Hyundai', 'year': 2012, 'model': 'Tucson', 'price': 9800, 'mileage': 175000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Hyundai i20 Active', 'brand': 'Hyundai', 'year': 2015, 'model': 'i20', 'price': 8500, 'mileage': 125000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
        ]
        
        # Mitsubishi samples
        mitsubishi_samples = [
            {'title': '2013 Mitsubishi Lancer ES', 'brand': 'Mitsubishi', 'year': 2013, 'model': 'Lancer', 'price': 8500, 'mileage': 165000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Mitsubishi Outlander LS', 'brand': 'Mitsubishi', 'year': 2014, 'model': 'Outlander', 'price': 11200, 'mileage': 145000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Mitsubishi ASX LS', 'brand': 'Mitsubishi', 'year': 2012, 'model': 'ASX', 'price': 9800, 'mileage': 175000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Mitsubishi Mirage ES', 'brand': 'Mitsubishi', 'year': 2015, 'model': 'Mirage', 'price': 7500, 'mileage': 125000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
        ]
        
        # Volkswagen samples
        volkswagen_samples = [
            {'title': '2013 Volkswagen Golf Trendline', 'brand': 'Volkswagen', 'year': 2013, 'model': 'Golf', 'price': 11200, 'mileage': 145000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Volkswagen Passat Comfortline', 'brand': 'Volkswagen', 'year': 2014, 'model': 'Passat', 'price': 11800, 'mileage': 135000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Volkswagen Tiguan Trendline', 'brand': 'Volkswagen', 'year': 2012, 'model': 'Tiguan', 'price': 10800, 'mileage': 165000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
            {'title': '2015 Volkswagen Polo Trendline', 'brand': 'Volkswagen', 'year': 2015, 'model': 'Polo', 'price': 9800, 'mileage': 115000, 'location': 'Hamilton', 'scraped_date': '2025-09-15'},
        ]
        
        # BMW samples
        bmw_samples = [
            {'title': '2013 BMW 320i', 'brand': 'BMW', 'year': 2013, 'model': '3 Series', 'price': 12500, 'mileage': 155000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 BMW 520i', 'brand': 'BMW', 'year': 2014, 'model': '5 Series', 'price': 12500, 'mileage': 135000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 BMW X3 xDrive20d', 'brand': 'BMW', 'year': 2012, 'model': 'X3', 'price': 12500, 'mileage': 175000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
        ]
        
        # Audi samples
        audi_samples = [
            {'title': '2013 Audi A3 Sportback', 'brand': 'Audi', 'year': 2013, 'model': 'A3', 'price': 12200, 'mileage': 145000, 'location': 'Auckland', 'scraped_date': '2025-09-15'},
            {'title': '2014 Audi A4 Avant', 'brand': 'Audi', 'year': 2014, 'model': 'A4', 'price': 12500, 'mileage': 135000, 'location': 'Wellington', 'scraped_date': '2025-09-15'},
            {'title': '2012 Audi Q5', 'brand': 'Audi', 'year': 2012, 'model': 'Q5', 'price': 11800, 'mileage': 165000, 'location': 'Christchurch', 'scraped_date': '2025-09-15'},
        ]
        
        # Combine all samples
        sample_data.extend(subaru_samples)
        sample_data.extend(toyota_samples)
        sample_data.extend(honda_samples)
        sample_data.extend(mazda_samples)
        sample_data.extend(ford_samples)
        sample_data.extend(nissan_samples)
        sample_data.extend(hyundai_samples)
        sample_data.extend(mitsubishi_samples)
        sample_data.extend(volkswagen_samples)
        sample_data.extend(bmw_samples)
        sample_data.extend(audi_samples)
        
        return sample_data

    def analyze_data(self):
        """Create DataFrame and add fuel efficiency data"""
        if not self.listings:
            print("No listings to analyze!")
            return None
            
        df = pd.DataFrame(self.listings)
        
        # Add fuel efficiency
        df['fuel_efficiency_l_100km'] = df.apply(
            lambda row: self.get_fuel_efficiency(row['brand'], row['model'], row['year']) if row['year'] else None,
            axis=1
        )
        
        # Calculate annual fuel cost (assuming 15,000km/year at $2.40/L)
        df['annual_fuel_cost'] = df['fuel_efficiency_l_100km'] * 150 * 2.40
        
        # Filter for budget criteria
        df_filtered = df[
            (df['price'] >= 7500) &
            (df['price'] <= 12500) &
            (df['price'] > 0) &
            (df['mileage'].notna()) &
            (df['mileage'] <= 250000)
        ].copy()
        
        # Add value score (lower is better)
        df_filtered['fuel_efficiency_filled'] = df_filtered['fuel_efficiency_l_100km'].fillna(10.0)
        df_filtered['value_score'] = (
            df_filtered['price'] / 1000 +
            df_filtered['mileage'] / 10000 +
            df_filtered['fuel_efficiency_filled'] * 2
        )
        
        # Add additional analysis columns
        df_filtered['price_per_km'] = df_filtered['price'] / df_filtered['mileage']
        df_filtered['age_years'] = 2025 - df_filtered['year']
        df_filtered['mileage_per_year'] = df_filtered['mileage'] / df_filtered['age_years']
        
        return df_filtered.sort_values('value_score')

    def save_dataset(self, df):
        """Save the dataset to CSV"""
        if df is not None and not df.empty:
            df.to_csv(self.dataset_file, index=False)
            print(f"\nDataset saved to '{self.dataset_file}'")
            print(f"Total records: {len(df)}")
            print(f"Brands included: {sorted(df['brand'].unique())}")
            print(f"Price range: ${df['price'].min():,} - ${df['price'].max():,}")
            print(f"Year range: {df['year'].min()} - {df['year'].max()}")
            return True
        else:
            print("No data to save!")
            return False

    def get_dataset_summary(self, df):
        """Get summary statistics of the dataset"""
        if df is None or df.empty:
            print("No data to summarize!")
            return
            
        print("\n" + "="*60)
        print("CAR DATASET SUMMARY")
        print("="*60)
        
        print(f"Total listings: {len(df)}")
        print(f"Brands: {', '.join(sorted(df['brand'].unique()))}")
        print(f"Price range: ${df['price'].min():,} - ${df['price'].max():,}")
        print(f"Year range: {df['year'].min()} - {df['year'].max()}")
        print(f"Average mileage: {df['mileage'].mean():,.0f} km")
        
        print("\nTop 10 Best Value Cars:")
        print("-" * 40)
        top_10 = df.head(10)[['brand', 'model', 'year', 'price', 'mileage', 'value_score']]
        for idx, row in top_10.iterrows():
            print(f"{row['year']} {row['brand']} {row['model']} - ${row['price']:,} ({row['mileage']:,}km) - Score: {row['value_score']:.1f}")
        
        print(f"\nFuel Efficiency Summary:")
        fuel_data = df['fuel_efficiency_l_100km'].dropna()
        if not fuel_data.empty:
            print(f"Best efficiency: {fuel_data.min():.1f} L/100km")
            print(f"Average efficiency: {fuel_data.mean():.1f} L/100km")
            print(f"Worst efficiency: {fuel_data.max():.1f} L/100km")
        else:
            print("No fuel efficiency data available")

# Usage example
if __name__ == "__main__":
    try:
        analyzer = CarAnalyzer()
        
        # Create sample data for demonstration
        print("Creating comprehensive car dataset...")
        analyzer.listings = analyzer.create_sample_data()
        
        # Analyze the data
        df_analyzed = analyzer.analyze_data()
        
        if df_analyzed is not None and not df_analyzed.empty:
            # Save dataset
            analyzer.save_dataset(df_analyzed)
            
            # Show summary
            analyzer.get_dataset_summary(df_analyzed)
            
        else:
            print("No valid data to analyze!")
            
    except ImportError as e:
        print(f"Missing required packages: {e}")
        print("Please install required packages using: pip install -r requirements.txt")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your data and try again.")
