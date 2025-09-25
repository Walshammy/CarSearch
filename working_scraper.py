from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
from datetime import datetime
import logging

class SimpleTradeMeScraper:
    def __init__(self):
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # URLs to scrape
        self.urls = {
            'Toyota 86': 'https://www.trademe.co.nz/a/motors/cars/toyota/86',
            'Subaru BRZ': 'https://www.trademe.co.nz/a/motors/cars/subaru/brz'
        }
        
        # Output directory
        self.output_dir = r"C:\Users\james\Downloads\CarSearch"
        os.makedirs(self.output_dir, exist_ok=True)

    def scrape_car_listings(self, car_model, url):
        """Scrape listings for a specific car model"""
        self.logger.info(f"Starting scrape for {car_model}")
        
        driver = webdriver.Chrome(options=self.chrome_options)
        all_listings = []
        
        try:
            # Navigate to the page
            driver.get(url)
            self.logger.info(f"Navigated to: {url}")
            
            # Wait for page to load completely
            time.sleep(10)
            
            # Get page title to confirm we're on the right page
            title = driver.title
            self.logger.info(f"Page title: {title}")
            
            # Look for listings using multiple approaches
            listings_found = False
            
            # Method 1: Look for the specific TradeMe listing class
            try:
                listings = driver.find_elements(By.CSS_SELECTOR, '.tm-motors-tier-one-search-card__listing-details-container')
                if listings:
                    self.logger.info(f"Found {len(listings)} listings using TradeMe selector")
                    listings_found = True
            except Exception as e:
                self.logger.warning(f"TradeMe selector failed: {e}")
            
            # Method 2: Look for any elements containing listing text
            if not listings_found:
                try:
                    listings = driver.find_elements(By.XPATH, "//div[contains(text(), 'Toyota 86') or contains(text(), 'Subaru BRZ')]")
                    if listings:
                        self.logger.info(f"Found {len(listings)} listings using text search")
                        listings_found = True
                except Exception as e:
                    self.logger.warning(f"Text search failed: {e}")
            
            # Method 3: Look for any div elements and filter by content
            if not listings_found:
                try:
                    all_divs = driver.find_elements(By.TAG_NAME, 'div')
                    listings = []
                    for div in all_divs:
                        text = div.text.strip()
                        if text and (car_model.split()[0] in text or car_model.split()[1] in text) and len(text) > 50:
                            listings.append(div)
                    if listings:
                        self.logger.info(f"Found {len(listings)} listings using div filtering")
                        listings_found = True
                except Exception as e:
                    self.logger.warning(f"Div filtering failed: {e}")
            
            if not listings_found:
                self.logger.warning(f"No listings found for {car_model}")
                return all_listings
            
            # Extract data from each listing
            for i, listing in enumerate(listings[:20]):  # Limit to first 20 listings
                try:
                    listing_data = self.extract_listing_data(listing, car_model)
                    if listing_data:
                        all_listings.append(listing_data)
                        self.logger.info(f"Extracted listing {i+1}: {listing_data.get('title', 'N/A')[:50]}...")
                except Exception as e:
                    self.logger.error(f"Error processing listing {i+1}: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(all_listings)} listings for {car_model}")
            
        except Exception as e:
            self.logger.error(f"Error scraping {car_model}: {e}")
        
        finally:
            driver.quit()
        
        return all_listings

    def extract_listing_data(self, listing_element, car_model):
        """Extract data from a single listing element"""
        try:
            data = {}
            
            # Get the full text content
            full_text = listing_element.text.strip()
            
            if not full_text or len(full_text) < 20:
                return None
            
            # Split into lines
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            # First line is usually the title
            data['title'] = lines[0] if lines else 'N/A'
            
            # Look for price
            price_text = 'N/A'
            for line in lines:
                if '$' in line and any(char.isdigit() for char in line):
                    price_text = line
                    break
            data['price'] = price_text
            
            # Look for location
            location_text = 'N/A'
            for line in lines:
                if any(word in line.lower() for word in ['city', 'auckland', 'wellington', 'christchurch', 'hamilton', 'tauranga', 'dunedin']):
                    location_text = line
                    break
            data['location'] = location_text
            
            # Look for mileage
            mileage_text = 'N/A'
            for line in lines:
                if 'km' in line.lower() and any(char.isdigit() for char in line):
                    mileage_text = line
                    break
            data['mileage'] = mileage_text
            
            # Extract year from title
            year = 'N/A'
            if data['title'] != 'N/A':
                words = data['title'].split()
                for word in words:
                    if word.isdigit() and len(word) == 4 and 1900 < int(word) < 2030:
                        year = word
                        break
            data['year'] = year
            
            # Set other fields
            data['car_model'] = car_model
            data['listing_url'] = 'N/A'
            data['listing_id'] = 'N/A'
            data['transmission'] = 'N/A'
            data['fuel_type'] = 'N/A'
            data['body_style'] = 'N/A'
            data['scrape_date'] = datetime.now().strftime('%Y-%m-%d')
            data['scrape_time'] = datetime.now().strftime('%H:%M:%S')
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error extracting listing data: {e}")
            return None

    def scrape_all_cars(self):
        """Scrape listings for all car models"""
        all_data = []
        
        for car_model, url in self.urls.items():
            listings = self.scrape_car_listings(car_model, url)
            all_data.extend(listings)
            time.sleep(2)  # Delay between requests
        
        return all_data

    def save_to_excel(self, data):
        """Save scraped data to Excel file"""
        if not data:
            self.logger.warning("No data to save")
            return
        
        df = pd.DataFrame(data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"trademe_cars_{timestamp}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
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
        self.logger.info("Starting Trade Me car scraping")
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
    scraper = SimpleTradeMeScraper()
    scraper.run()

if __name__ == "__main__":
    main()
