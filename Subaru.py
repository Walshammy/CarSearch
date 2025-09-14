import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class SubaruAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Fuel efficiency data (L/100km) - based on official specs and real-world data
        self.fuel_efficiency = {
            'impreza': {'2008-2012': 8.5, '2012-2016': 7.8, '2017+': 7.2},
            'xv': {'2012-2016': 8.2, '2017+': 7.5},
            'crosstrek': {'2012-2016': 8.2, '2017+': 7.5},  # Same as XV
            'forester': {'2008-2012': 9.8, '2013-2018': 8.9, '2019+': 8.4},
            'outback': {'2009-2014': 10.2, '2015-2019': 8.7, '2020+': 8.1},
            'legacy': {'2009-2014': 9.8, '2015-2019': 8.9, '2020+': 8.3},
            'brz': {'2012+': 8.8},
            'wrx': {'2008-2014': 11.5, '2015+': 10.2},
            'sti': {'all': 13.0}
        }
        
        self.base_url = "https://www.trademe.co.nz/a/motors/cars/subaru"
        self.listings = []

    def get_fuel_efficiency(self, model, year):
        """Get fuel efficiency for a specific model and year"""
        model_lower = model.lower()
        
        # Handle model name variations
        if 'xv' in model_lower or 'crosstrek' in model_lower:
            model_key = 'xv'
        elif 'impreza' in model_lower:
            model_key = 'impreza'
        elif 'forester' in model_lower:
            model_key = 'forester'
        elif 'outback' in model_lower:
            model_key = 'outback'
        elif 'legacy' in model_lower:
            model_key = 'legacy'
        elif 'brz' in model_lower:
            model_key = 'brz'
        elif 'wrx' in model_lower and 'sti' not in model_lower:
            model_key = 'wrx'
        elif 'sti' in model_lower:
            model_key = 'sti'
        else:
            return None
            
        if model_key not in self.fuel_efficiency:
            return None
        
        # Determine year range
        efficiency_data = self.fuel_efficiency[model_key]
        
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
            return efficiency_data.get('all', 11.0)  # Default for older cars

    def scrape_listings(self, max_price=12500, max_pages=5):
        """Scrape Subaru listings from Trade Me"""
        print("Scraping Subaru listings from Trade Me...")
        
        for page in range(1, max_pages + 1):
            print(f"Scraping page {page}...")
            
            params = {
                'price_max': max_price,
                'page': page
            }
            
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find listing containers (this may need adjustment based on Trade Me's current structure)
                listings = soup.find_all('div', class_='listing-item') or soup.find_all('article')
                
                if not listings:
                    print(f"No listings found on page {page}, stopping...")
                    break
                
                for listing in listings:
                    try:
                        listing_data = self.extract_listing_data(listing)
                        if listing_data:
                            self.listings.append(listing_data)
                    except Exception as e:
                        print(f"Error extracting listing: {e}")
                        continue
                
                # Be respectful with scraping
                time.sleep(2)
                
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue
        
        print(f"Scraped {len(self.listings)} listings")
        return self.listings

    def extract_listing_data(self, listing):
        """Extract data from a single listing"""
        try:
            # This is a template - you'll need to adjust selectors based on Trade Me's structure
            title_elem = listing.find('h3') or listing.find('a', class_='listing-title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            price_elem = listing.find(class_=re.compile('price|amount'))
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price = self.extract_price(price_text)
            
            # Extract year and model from title
            year, model = self.extract_year_model(title)
            
            # Look for mileage/odometer
            mileage_elem = listing.find(text=re.compile(r'\d+,?\d*\s*km'))
            mileage = self.extract_mileage(mileage_elem) if mileage_elem else None
            
            return {
                'title': title,
                'year': year,
                'model': model,
                'price': price,
                'mileage': mileage,
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

    def extract_year_model(self, title):
        """Extract year and model from title"""
        # Look for year (4 digits)
        year_match = re.search(r'(19|20)\d{2}', title)
        year = int(year_match.group()) if year_match else None
        
        # Look for model names
        title_lower = title.lower()
        if 'xv' in title_lower or 'crosstrek' in title_lower:
            model = 'XV/Crosstrek'
        elif 'impreza' in title_lower:
            model = 'Impreza'
        elif 'forester' in title_lower:
            model = 'Forester'
        elif 'outback' in title_lower:
            model = 'Outback'
        elif 'legacy' in title_lower:
            model = 'Legacy'
        elif 'brz' in title_lower:
            model = 'BRZ'
        elif 'wrx' in title_lower and 'sti' not in title_lower:
            model = 'WRX'
        elif 'sti' in title_lower:
            model = 'WRX STI'
        else:
            model = 'Other'
            
        return year, model

    def extract_mileage(self, mileage_text):
        """Extract numeric mileage from text"""
        if isinstance(mileage_text, str):
            numbers = re.findall(r'[\d,]+', mileage_text)
            if numbers:
                return int(numbers[0].replace(',', ''))
        return None

    def analyze_data(self):
        """Create DataFrame and add fuel efficiency data"""
        if not self.listings:
            print("No listings to analyze!")
            return None
            
        df = pd.DataFrame(self.listings)
        
        # Add fuel efficiency
        df['fuel_efficiency_l_100km'] = df.apply(
            lambda row: self.get_fuel_efficiency(row['model'], row['year']) if row['year'] else None,
            axis=1
        )
        
        # Calculate annual fuel cost (assuming 15,000km/year at $2.40/L)
        df['annual_fuel_cost'] = df['fuel_efficiency_l_100km'] * 150 * 2.40
        
        # Filter for your criteria
        df_filtered = df[
            (df['price'] <= 12500) &
            (df['price'] > 0) &
            (df['mileage'].notna()) &
            (df['mileage'] <= 200000)
        ].copy()
        
        # Add value score (lower is better)
        # Handle NaN values in fuel efficiency by using a default value
        df_filtered['fuel_efficiency_filled'] = df_filtered['fuel_efficiency_l_100km'].fillna(10.0)
        df_filtered['value_score'] = (
            df_filtered['price'] / 1000 +
            df_filtered['mileage'] / 10000 +
            df_filtered['fuel_efficiency_filled'] * 2
        )
        
        return df_filtered.sort_values('value_score')

    def create_visualizations(self, df):
        """Create analysis visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Price vs Mileage by Model
        sns.scatterplot(data=df, x='mileage', y='price', hue='model', ax=axes[0, 0])
        axes[0, 0].set_title('Price vs Mileage by Model')
        axes[0, 0].set_xlabel('Mileage (km)')
        axes[0, 0].set_ylabel('Price ($)')
        
        # Fuel Efficiency by Model
        sns.boxplot(data=df, x='model', y='fuel_efficiency_l_100km', ax=axes[0, 1])
        axes[0, 1].set_title('Fuel Efficiency by Model')
        axes[0, 1].set_ylabel('Fuel Efficiency (L/100km)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Annual Fuel Cost Distribution
        sns.histplot(data=df, x='annual_fuel_cost', bins=20, ax=axes[1, 0])
        axes[1, 0].set_title('Annual Fuel Cost Distribution')
        axes[1, 0].set_xlabel('Annual Fuel Cost ($)')
        
        # Value Score vs Price
        sns.scatterplot(data=df, x='price', y='value_score', hue='model', ax=axes[1, 1])
        axes[1, 1].set_title('Value Score vs Price (Lower Score = Better Value)')
        axes[1, 1].set_xlabel('Price ($)')
        axes[1, 1].set_ylabel('Value Score')
        
        plt.tight_layout()
        plt.show()

    def get_recommendations(self, df, top_n=10):
        """Get top recommendations based on your criteria"""
        recommendations = df.head(top_n)[
            ['title', 'year', 'model', 'price', 'mileage',
             'fuel_efficiency_l_100km', 'annual_fuel_cost', 'value_score']
        ].round(2)
        
        return recommendations

# Usage example
if __name__ == "__main__":
    try:
        analyzer = SubaruAnalyzer()
        
        # Scrape listings (you may need to adjust selectors for current Trade Me structure)
        # analyzer.scrape_listings(max_price=12500, max_pages=3)
        
        # For testing, create sample data
        sample_data = [
            {'title': '2014 Subaru XV 2.0i', 'year': 2014, 'model': 'XV/Crosstrek', 'price': 11500, 'mileage': 145000, 'scraped_date': '2025-09-15'},
            {'title': '2013 Subaru Impreza XV', 'year': 2013, 'model': 'XV/Crosstrek', 'price': 10200, 'mileage': 165000, 'scraped_date': '2025-09-15'},
            {'title': '2012 Subaru Forester 2.5X', 'year': 2012, 'model': 'Forester', 'price': 9800, 'mileage': 175000, 'scraped_date': '2025-09-15'},
            {'title': '2015 Subaru Impreza 2.0i', 'year': 2015, 'model': 'Impreza', 'price': 12000, 'mileage': 125000, 'scraped_date': '2025-09-15'},
            {'title': '2011 Subaru Outback 2.5i', 'year': 2011, 'model': 'Outback', 'price': 8900, 'mileage': 185000, 'scraped_date': '2025-09-15'},
        ]
        
        analyzer.listings = sample_data
        
        # Analyze the data
        df_analyzed = analyzer.analyze_data()
        
        if df_analyzed is not None and not df_analyzed.empty:
            print("\nTop Subaru Recommendations:")
            print("="*50)
            recommendations = analyzer.get_recommendations(df_analyzed)
            print(recommendations.to_string(index=False))
            
            print("\nFuel Efficiency Summary:")
            fuel_data = df_analyzed['fuel_efficiency_l_100km'].dropna()
            if not fuel_data.empty:
                print(f"Best efficiency: {fuel_data.min():.1f} L/100km")
                print(f"Average efficiency: {fuel_data.mean():.1f} L/100km")
            else:
                print("No fuel efficiency data available")
            
            # Create visualizations
            analyzer.create_visualizations(df_analyzed)
            
            # Export to CSV for further analysis
            df_analyzed.to_csv('subaru_analysis.csv', index=False)
            print("\nData exported to 'subaru_analysis.csv'")
        else:
            print("No valid data to analyze!")
            
    except ImportError as e:
        print(f"Missing required packages: {e}")
        print("Please install required packages using: pip install -r requirements.txt")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your data and try again.")