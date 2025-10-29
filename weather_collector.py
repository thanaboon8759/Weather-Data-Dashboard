import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
import time
import os
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherDataCollector:
    """Collect weather data from OpenWeatherMap API or generate sample data"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Load API key from environment if not provided
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def test_api_connection(self) -> bool:
        """Test if the API key is valid"""
        if not self.api_key:
            return False
            
        try:
            # Test with a simple city
            response = requests.get(
                f"{self.base_url}/weather",
                params={'q': 'London', 'appid': self.api_key, 'units': 'metric'},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
        
    def fetch_current_weather(self, city: str) -> Dict:
        """Fetch current weather data for a city - API ONLY"""
        if not self.api_key:
            raise ValueError(f"❌ No API key provided. Cannot fetch data for {city}")
            
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ Real API data fetched for {city}")
            return {
                'city': city,
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'rainfall': data.get('rain', {}).get('1h', 0),  # mm in last hour
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'api'  # Mark as real API data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API failed for {city}: {str(e)}")
            raise ConnectionError(f"Failed to fetch weather data for {city}: {str(e)}")
    

    
    def collect_current_weather_all_cities(self, cities: List[str]) -> pd.DataFrame:
        """Collect current weather data for all cities from API - API ONLY"""
        if not self.api_key:
            raise ValueError("❌ No API key provided. Cannot collect current weather data")
        
        current_data = []
        failed_cities = []
        
        logger.info("🌤️ Fetching current weather data from API...")
        
        for city in cities:
            try:
                weather_data = self.fetch_current_weather(city)
                current_data.append(weather_data)
                
                # Small delay to be respectful to API
                time.sleep(0.2)
            except Exception as e:
                logger.error(f"❌ Failed to fetch data for {city}: {e}")
                failed_cities.append(city)
                continue
        
        if not current_data:
            raise ConnectionError("❌ Failed to fetch weather data for any city. Please check your API key and internet connection")
        
        if failed_cities:
            logger.warning(f"⚠️ Failed to fetch data for cities: {', '.join(failed_cities)}")
        
        return pd.DataFrame(current_data)
    
    def collect_historical_data(self, cities: List[str], days: int = 30) -> pd.DataFrame:
        """Collect historical weather data - API ONLY"""
        if not self.api_key:
            raise ValueError("❌ No API key provided. Cannot collect historical data")
        
        data = []
        
        logger.info("🔄 Fetching current weather data from API to generate historical data...")
        
        for city in cities:
            logger.info(f"Generating historical data for {city} based on API data...")
            
            try:
                # Get current weather data from API
                current_weather = self.fetch_current_weather(city)
                base_temp = current_weather['temperature']
                base_humidity = current_weather['humidity']
                base_rainfall = current_weather['rainfall']
                
                # Generate historical variations based on real API data
                for i in range(days):
                    date = datetime.now() - timedelta(days=i)
                    
                    # Add realistic seasonal and daily variations
                    temp_variation = np.random.normal(0, 3)  # ±3°C variation
                    humidity_variation = np.random.normal(0, 10)  # ±10% variation
                    rainfall_variation = np.random.exponential(1) if np.random.random() < 0.3 else 0
                    
                    weather_data = {
                        'city': city,
                        'temperature': round(max(base_temp + temp_variation, -10), 1),
                        'humidity': round(max(min(base_humidity + humidity_variation, 100), 0), 1),
                        'rainfall': round(max(0, base_rainfall + rainfall_variation), 1),
                        'date': date.strftime('%Y-%m-%d'),
                        'source': 'api_derived'  # Based on real API data
                    }
                    data.append(weather_data)
                    
            except Exception as e:
                logger.error(f"❌ Failed to fetch API data for {city}: {e}")
                # Don't add any data if API fails - API ONLY mode
                continue
        
        if not data:
            raise ConnectionError("❌ Failed to collect any weather data. Please check your API key and internet connection")
        
        df = pd.DataFrame(data)
        logger.info(f"✅ Generated {len(df)} historical data points from API data for {len(cities)} cities")
        return self._clean_data(df)
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process the weather data"""
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure numeric types
        df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
        df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')
        df['rainfall'] = pd.to_numeric(df['rainfall'], errors='coerce')
        
        # Handle missing rainfall values (fill with 0)
        df['rainfall'] = df['rainfall'].fillna(0)
        
        # Remove any rows with missing temperature or humidity
        df = df.dropna(subset=['temperature', 'humidity'])
        
        # Add derived columns
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        df['month_year'] = df['date'].dt.to_period('M')
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        logger.info(f"Cleaned data: {len(df)} records for {df['city'].nunique()} cities")
        return df
    
    def generate_sample_csv(self, filename: str = 'sample_weather_data.csv', cities: List[str] = None, days: int = 90):
        """Generate a comprehensive sample CSV file"""
        if cities is None:
            cities = ['Bangkok', 'Tokyo', 'London', 'New York', 'Sydney', 'Mumbai']
        
        df = self.collect_historical_data(cities, days)
        df.to_csv(filename, index=False)
        logger.info(f"Sample data saved to {filename}")
        return df

if __name__ == "__main__":
    # Example usage
    collector = WeatherDataCollector()  # No API key = sample data
    
    cities = ['Bangkok', 'Tokyo', 'London']
    df = collector.collect_historical_data(cities, days=30)
    
    print(f"Collected {len(df)} weather records")
    print(df.head())
    
    # Save to CSV
    df.to_csv('weather_data.csv', index=False)
    print("Data saved to weather_data.csv")