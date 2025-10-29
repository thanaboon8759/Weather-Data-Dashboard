# Weather Data Dashboard

A simple weather analytics platform that collects real-time data from the OpenWeatherMap API and provides interactive visualizations.

## Features

- Real-time weather data collection from OpenWeatherMap API
- Interactive web dashboard with clean interface
- Weather analytics and visualizations
- Data filtering by city and date range
- Multiple chart types (line charts, bar charts, scatter plots)

## Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection for API access
- OpenWeatherMap API key (free registration required)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/thanaboon8759/Weather-Data-Dashboard.git
   cd Weather-Data-Dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API access**
   - Register for a free API key at [OpenWeatherMap](https://openweathermap.org/api)
   - Create a `.env` file in the project root
   - Add your API key: `OPENWEATHER_API_KEY=your_api_key_here`

4. **Launch the application**
   ```bash
   streamlit run weather_dashboard.py
   ```

## Components

- **weather_dashboard.py** - Main web interface built with Streamlit
- **weather_collector.py** - API data collection module
- **weather_analyzer.py** - Data analysis and visualization engine
- **requirements.txt** - Python dependency specifications
- **.env** - Environment configuration for API keys

## Data Sources

- **Primary**: OpenWeatherMap API for real-time weather data
- **Coverage**: Multiple global cities including London, Tokyo, New York, Bangkok, Sydney, and Mumbai
- **Data Points**: Temperature, humidity, rainfall, and atmospheric conditions

## Usage

The web dashboard provides:
- Interactive data filtering by city and date range
- Multiple visualization types (temperature trends, rainfall analysis, humidity correlations)
- Real-time data updates
- Professional chart presentation with customizable display options

## System Requirements

- **Memory**: Minimum 512MB RAM
- **Storage**: 50MB available disk space
- **Network**: Stable internet connection for API access
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

## License

This project is licensed under the MIT License. See the LICENSE file for details.