# Car Search Dataset Generator

A comprehensive Python tool for creating car datasets with fuel efficiency analysis for the New Zealand market.

## Features

- **Multi-Brand Support**: Analyzes cars from 11+ major brands including Toyota, Honda, Mazda, Subaru, Ford, Nissan, Hyundai, Mitsubishi, Volkswagen, BMW, and Audi
- **Fuel Efficiency Data**: Comprehensive fuel consumption data (L/100km) for different model years
- **Budget Filtering**: Focuses on cars in the $7,500 - $12,500 price range
- **Value Scoring**: Calculates value scores based on price, mileage, and fuel efficiency
- **Dataset Export**: Exports data to CSV format for further analysis

## Files

- `CarAnalyzer.py` - Main analyzer class with comprehensive car data
- `generate_dataset.py` - Simple script to generate the dataset
- `Subaru.py` - Original Subaru-specific analyzer (legacy)
- `requirements.txt` - Python dependencies
- `car_dataset.csv` - Generated dataset output

## Usage

### Quick Start
```bash
python generate_dataset.py
```

### Using the Analyzer Class
```python
from CarAnalyzer import CarAnalyzer

# Create analyzer
analyzer = CarAnalyzer()

# Generate sample data
analyzer.listings = analyzer.create_sample_data()

# Analyze and save
df = analyzer.analyze_data()
analyzer.save_dataset(df)
```

## Dataset Columns

- `title` - Full car title/description
- `brand` - Car manufacturer
- `year` - Model year
- `model` - Car model
- `price` - Price in NZD
- `mileage` - Odometer reading in km
- `location` - Geographic location
- `fuel_efficiency_l_100km` - Fuel consumption (L/100km)
- `annual_fuel_cost` - Estimated annual fuel cost
- `value_score` - Calculated value score (lower is better)
- `price_per_km` - Price per kilometer driven
- `age_years` - Car age in years
- `mileage_per_year` - Average annual mileage

## Sample Output

The dataset includes 44+ sample cars across 11 brands with:
- Price range: $7,500 - $12,500
- Year range: 2011 - 2015
- Average mileage: ~149,000 km
- Fuel efficiency: 4.2 - 12.8 L/100km

## Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

## Future Enhancements

- Real-time web scraping from Trade Me
- Additional car brands and models
- More detailed analysis metrics
- Visualization capabilities
- Price trend analysis
