from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import os
from datetime import datetime
import logging
import random

class TradeMeCarScraperSelenium:
    def __init__(self):
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # Run in background
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Base URLs for the car models
        self.urls = {
            'Toyota 86': 'https://www.trademe.co.nz/a/motors/cars/toyota/86',
            'Subaru BRZ': 'https://www.trademe.co.nz/a/motors/cars/subaru/brz'
        }
        
        # Output directory
        self.output_dir = r"C:\Users\james\Downloads\CarSearch"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.driver = None

    def setup_driver(self):
        """Initialize the Chrome driver"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.implicitly_wait(10)
            self.logger.info("Chrome driver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            return False

    def wait_for_listings(self, timeout=15):
        """Wait for listings to load on the page"""
        try:
            # Wait for TradeMe listing elements to appear
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.tm-motors-tier-one-search-card__listing-details-container'))
            )
            return True
        except TimeoutException:
            self.logger.warning("No listings found within timeout period")
            return False

    def extract_listing_data(self, listing_element):
        """Extract data from a single listing element"""
        try:
            data = {}
            
            # Get the full text content of the listing
            full_text = listing_element.text.strip()
            
            # Split into lines for easier parsing
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            # First line is usually the title
            data['title'] = lines[0] if lines else 'N/A'
            
            # Look for price (usually contains $)
            price_text = 'N/A'
            for line in lines:
                if '$' in line and any(char.isdigit() for char in line):
                    price_text = line
                    break
            data['price'] = price_text
            
            # Look for location (usually contains city names)
            location_text = 'N/A'
            for line in lines:
                if any(word in line.lower() for word in ['city', 'auckland', 'wellington', 'christchurch', 'hamilton', 'tauranga', 'dunedin', 'palmerston', 'nelson', 'rotorua', 'napier', 'hastings', 'new plymouth', 'whangarei', 'invercargill', 'upper hutt', 'lower hutt', 'porirua', 'kapiti', 'manawatu', 'wanganui', 'gisborne', 'timaru', 'masterton', 'levin', 'feilding', 'ashburton', 'rangiora', 'rolleston', 'blenheim', 'queenstown', 'wanaka', 'gore', 'balclutha', 'oamaru', 'westport', 'greymouth', 'kaikoura', 'motueka', 'richmond', 'takaka', 'collingwood', 'picton', 'hokitika', 'reefton', 'cromwell', 'alexandra', 'roxburgh', 'lawrence', 'milton', 'kaitangata', 'clinton', 'wyndham', 'edendale', 'mataura', 'gore', 'balfour', 'lumsden', 'garston', 'athol', 'kingston', 'te anau', 'manapouri', 'riverton', 'colac bay', 'oyster bay', 'bluff', 'invercargill']):
                    location_text = line
                    break
            data['location'] = location_text
            
            # Look for mileage (usually contains 'km')
            mileage_text = 'N/A'
            for line in lines:
                if 'km' in line.lower() and any(char.isdigit() for char in line):
                    mileage_text = line
                    break
            data['mileage'] = mileage_text
            
            # Try to find listing URL by looking for parent elements
            url_text = 'N/A'
            try:
                # Look for the parent card element that should contain the link
                parent_card = listing_element.find_element(By.XPATH, './ancestor::*[contains(@class, "search-card")]')
                link_elem = parent_card.find_element(By.TAG_NAME, 'a')
                url_text = link_elem.get_attribute('href') or 'N/A'
            except NoSuchElementException:
                pass
            
            data['listing_url'] = url_text
            
            # Extract listing ID from URL
            if url_text != 'N/A' and '/' in url_text:
                data['listing_id'] = url_text.split('/')[-1] if url_text.split('/')[-1] else 'N/A'
            else:
                data['listing_id'] = 'N/A'
            
            # Try to extract year from title
            year = 'N/A'
            if data['title'] != 'N/A':
                words = data['title'].split()
                for word in words:
                    if word.isdigit() and len(word) == 4 and 1900 < int(word) < 2030:
                        year = word
                        break
            data['year'] = year
            
            # Set default values for other fields
            data['transmission'] = 'N/A'
            data['fuel_type'] = 'N/A'
            data['body_style'] = 'N/A'
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error extracting listing data: {e}")
            return None

    def scrape_car_listings(self, car_model, base_url):
        """Scrape all listings for a specific car model"""
        all_listings = []
        
        self.logger.info(f"Starting scrape for {car_model}")
        
        try:
            # Navigate to the page
            self.driver.get(base_url)
            self.logger.info(f"Navigated to: {base_url}")
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for listings to appear
            if not self.wait_for_listings():
                self.logger.warning(f"No listings found for {car_model}")
                return all_listings
            
            # Use the correct TradeMe selector
            listing_selectors = [
                '.tm-motors-tier-one-search-card__listing-details-container'
            ]
            
            listings = []
            for selector in listing_selectors:
                try:
                    listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if listings:
                        self.logger.info(f"Found {len(listings)} listings using selector: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not listings:
                self.logger.warning(f"No listing elements found for {car_model}")
                return all_listings
            
            # Extract data from each listing
            for i, listing in enumerate(listings):
                try:
                    listing_data = self.extract_listing_data(listing)
                    if listing_data:
                        listing_data['car_model'] = car_model
                        listing_data['scrape_date'] = datetime.now().strftime('%Y-%m-%d')
                        listing_data['scrape_time'] = datetime.now().strftime('%H:%M:%S')
                        all_listings.append(listing_data)
                        self.logger.info(f"Extracted listing {i+1}: {listing_data.get('title', 'N/A')[:50]}...")
                except Exception as e:
                    self.logger.error(f"Error processing listing {i+1}: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(all_listings)} listings for {car_model}")
            
        except Exception as e:
            self.logger.error(f"Error scraping {car_model}: {e}")
        
        return all_listings

    def scrape_all_cars(self):
        """Scrape listings for all car models"""
        all_data = []
        
        if not self.setup_driver():
            return all_data
        
        try:
            for car_model, url in self.urls.items():
                listings = self.scrape_car_listings(car_model, url)
                all_data.extend(listings)
                
                # Delay between different car models
                time.sleep(random.uniform(2, 5))
        
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("Chrome driver closed")
        
        return all_data

    def save_to_excel(self, data):
        """Save scraped data to Excel file"""
        if not data:
            self.logger.warning("No data to save")
            return
        
        df = pd.DataFrame(data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"trademe_cars_selenium_{timestamp}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        # Reorder columns for better readability
        column_order = [
            'car_model', 'title', 'price', 'year', 'mileage', 
            'transmission', 'fuel_type', 'body_style', 'location',
            'listing_id', 'listing_url', 'scrape_date', 'scrape_time'
        ]
        
        # Only keep columns that exist in the data
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        try:
            df.to_excel(filepath, index=False, engine='openpyxl')
            self.logger.info(f"Data saved to: {filepath}")
            self.logger.info(f"Total listings scraped: {len(df)}")
            
            # Print summary
            print(f"\n=== Scraping Summary ===")
            print(f"Total listings: {len(df)}")
            for model in df['car_model'].unique():
                count = len(df[df['car_model'] == model])
                print(f"{model}: {count} listings")
            print(f"Data saved to: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving to Excel: {e}")

    def run(self):
        """Main execution method"""
        self.logger.info("Starting Trade Me car scraping with Selenium")
        start_time = datetime.now()
        
        try:
            # Scrape all car data
            data = self.scrape_all_cars()
            
            # Save to Excel
            self.save_to_excel(data)
            
            end_time = datetime.now()
            duration = end_time - start_time
            self.logger.info(f"Scraping completed in {duration}")
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")

def main():
    """Main function to run the scraper"""
    scraper = TradeMeCarScraperSelenium()
    scraper.run()

if __name__ == "__main__":
    main()
