import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class WeatherAnalyzer:
    """Analyze and visualize weather data with minimal color palette"""
    
    # Ultra-minimal Color Palette
    COLORS = {
        'temperature': '#F59E0B',  # Subtle orange
        'humidity': '#3B82F6',     # Clean blue  
        'rainfall': '#10B981',     # Fresh emerald
        'text': '#111827',         # Deep gray
        'grid': '#F3F4F6'          # Very light gray
    }
    
    # Clean color sequence for multiple cities
    CITY_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#6B7280', '#8B5CF6', '#EF4444']
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._validate_data()
    
    def _validate_data(self):
        """Validate that required columns exist"""
        required_cols = ['date', 'city', 'temperature', 'humidity', 'rainfall']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Ensure date is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df['date']):
            self.df['date'] = pd.to_datetime(self.df['date'])
    
    def calculate_summary_statistics(self) -> Dict:
        """Calculate comprehensive summary statistics"""
        stats = {}
        
        # Average temperature per city
        stats['avg_temp_by_city'] = self.df.groupby('city')['temperature'].mean().round(2)
        
        # Temperature statistics
        stats['temp_stats'] = {
            'overall_avg': round(self.df['temperature'].mean(), 2),
            'overall_max': round(self.df['temperature'].max(), 2),
            'overall_min': round(self.df['temperature'].min(), 2)
        }
        
        # Humidity statistics
        stats['humidity_stats'] = {
            'max_humidity': self.df.loc[self.df['humidity'].idxmax()],
            'min_humidity': self.df.loc[self.df['humidity'].idxmin()],
            'avg_humidity': round(self.df['humidity'].mean(), 2)
        }
        
        # Rainfall statistics
        self.df['month_year'] = self.df['date'].dt.to_period('M')
        stats['rainfall_by_month'] = self.df.groupby('month_year')['rainfall'].sum().round(2)
        
        # City-wise statistics
        city_stats = self.df.groupby('city').agg({
            'temperature': ['mean', 'min', 'max'],
            'humidity': ['mean', 'min', 'max'],
            'rainfall': ['sum', 'mean']
        }).round(2)
        stats['city_statistics'] = city_stats
        
        return stats
    
    def create_temperature_line_chart(self, cities: List[str] = None, 
                                      time_aggregation: str = "Daily",
                                      show_trend: bool = True) -> go.Figure:
        """Create interactive line chart for temperature vs date"""
        df_filtered = self.df.copy()
        
        if cities:
            df_filtered = df_filtered[df_filtered['city'].isin(cities)]
        
        # Apply time aggregation
        if time_aggregation == "Weekly":
            df_filtered = df_filtered.groupby(['city', pd.Grouper(key='date', freq='W')]).agg({
                'temperature': 'mean',
                'humidity': 'mean', 
                'rainfall': 'sum'
            }).reset_index()
        elif time_aggregation == "Monthly":
            df_filtered = df_filtered.groupby(['city', pd.Grouper(key='date', freq='M')]).agg({
                'temperature': 'mean',
                'humidity': 'mean',
                'rainfall': 'sum'
            }).reset_index()
        
        fig = px.line(
            df_filtered, 
            x='date', 
            y='temperature', 
            color='city',
            title='Temperature Trends Over Time',
            labels={'temperature': 'Temperature (°C)', 'date': 'Date'},
            hover_data=['humidity', 'rainfall'],
            color_discrete_sequence=self.CITY_COLORS
        )
        
        # Add trend lines if requested
        if show_trend:
            for i, city in enumerate(df_filtered['city'].unique()):
                city_data = df_filtered[df_filtered['city'] == city].copy()
                if len(city_data) > 1:
                    # Calculate trend line
                    x_numeric = pd.to_numeric(city_data['date'])
                    coeffs = np.polyfit(x_numeric, city_data['temperature'], 1)
                    trend_line = np.poly1d(coeffs)
                    
                    fig.add_trace(go.Scatter(
                        x=city_data['date'],
                        y=trend_line(x_numeric),
                        mode='lines',
                        name=f'{city} Trend',
                        line=dict(dash='dash', color=self.CITY_COLORS[i % len(self.CITY_COLORS)]),
                        showlegend=False
                    ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            legend_title="City",
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color=self.COLORS['text'],
            xaxis=dict(gridcolor=self.COLORS['grid']),
            yaxis=dict(gridcolor=self.COLORS['grid'])
        )
        
        return fig
    
    def create_static_temperature_chart(self, cities: List[str] = None, 
                                       time_aggregation: str = "Daily"):
        """Create static matplotlib chart for temperature"""
        df_filtered = self.df.copy()
        
        if cities:
            df_filtered = df_filtered[df_filtered['city'].isin(cities)]
        
        # Apply time aggregation
        if time_aggregation == "Weekly":
            df_filtered = df_filtered.groupby(['city', pd.Grouper(key='date', freq='W')]).agg({
                'temperature': 'mean'
            }).reset_index()
        elif time_aggregation == "Monthly":
            df_filtered = df_filtered.groupby(['city', pd.Grouper(key='date', freq='M')]).agg({
                'temperature': 'mean'
            }).reset_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for i, city in enumerate(df_filtered['city'].unique()):
            city_data = df_filtered[df_filtered['city'] == city]
            ax.plot(city_data['date'], city_data['temperature'], 
                   label=city, color=self.CITY_COLORS[i % len(self.CITY_COLORS)], 
                   linewidth=2)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title(f'Temperature Trends Over Time ({time_aggregation})')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def create_static_rainfall_chart(self, time_aggregation: str = "Monthly"):
        """Create static matplotlib chart for rainfall"""
        if time_aggregation == "Daily":
            grouped_data = self.df.groupby(['date', 'city'])['rainfall'].sum().reset_index()
        elif time_aggregation == "Weekly":
            grouped_data = self.df.groupby(['city', pd.Grouper(key='date', freq='W')])['rainfall'].sum().reset_index()
        else:  # Monthly
            grouped_data = self.df.groupby(['month_year', 'city'])['rainfall'].sum().reset_index()
            grouped_data = grouped_data.rename(columns={'month_year': 'date'})
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        cities = grouped_data['city'].unique()
        x_pos = np.arange(len(grouped_data['date'].unique()))
        width = 0.8 / len(cities)
        
        for i, city in enumerate(cities):
            city_data = grouped_data[grouped_data['city'] == city]
            ax.bar(x_pos + i * width, city_data['rainfall'], width, 
                  label=city, color=self.CITY_COLORS[i % len(self.CITY_COLORS)])
        
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Rainfall (mm)')
        ax.set_title(f'Total Rainfall by {time_aggregation}')
        ax.set_xticks(x_pos + width * (len(cities) - 1) / 2)
        ax.set_xticklabels([str(d)[:10] for d in grouped_data['date'].unique()], rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return fig
    
    def create_static_humidity_scatter(self, cities: List[str] = None, 
                                      time_aggregation: str = "Daily"):
        """Create static matplotlib scatter plot for humidity vs temperature"""
        df_filtered = self.df.copy()
        
        if cities:
            df_filtered = df_filtered[df_filtered['city'].isin(cities)]
        
        # Apply time aggregation
        if time_aggregation == "Weekly":
            df_filtered = df_filtered.groupby(['city', pd.Grouper(key='date', freq='W')]).agg({
                'temperature': 'mean',
                'humidity': 'mean'
            }).reset_index()
        elif time_aggregation == "Monthly":
            df_filtered = df_filtered.groupby(['city', pd.Grouper(key='date', freq='M')]).agg({
                'temperature': 'mean',
                'humidity': 'mean'
            }).reset_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for i, city in enumerate(df_filtered['city'].unique()):
            city_data = df_filtered[df_filtered['city'] == city]
            ax.scatter(city_data['temperature'], city_data['humidity'], 
                      label=city, color=self.CITY_COLORS[i % len(self.CITY_COLORS)], 
                      alpha=0.7, s=50)
        
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Humidity (%)')
        ax.set_title(f'Humidity vs Temperature Correlation ({time_aggregation})')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return fig
    
    def create_rainfall_bar_chart(self, time_aggregation: str = "Monthly") -> go.Figure:
        """Create bar chart for total rainfall per time period"""
        if time_aggregation == "Daily":
            grouped_data = self.df.groupby(['date', 'city'])['rainfall'].sum().reset_index()
            grouped_data['time_str'] = grouped_data['date'].dt.strftime('%Y-%m-%d')
        elif time_aggregation == "Weekly":
            grouped_data = self.df.groupby(['city', pd.Grouper(key='date', freq='W')])['rainfall'].sum().reset_index()
            grouped_data['time_str'] = grouped_data['date'].dt.strftime('%Y-W%U')
        else:  # Monthly
            grouped_data = self.df.groupby(['month_year', 'city'])['rainfall'].sum().reset_index()
            grouped_data['time_str'] = grouped_data['month_year'].astype(str)
            grouped_data = grouped_data.rename(columns={'month_year': 'date'})
        
        fig = px.bar(
            grouped_data,
            x='time_str',
            y='rainfall',
            color='city',
            title=f'Total Rainfall by {time_aggregation} and City',
            labels={'rainfall': 'Rainfall (mm)', 'time_str': 'Time Period'},
            barmode='group',
            color_discrete_sequence=self.CITY_COLORS
        )
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Rainfall (mm)",
            legend_title="City",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color=self.COLORS['text'],
            xaxis=dict(gridcolor=self.COLORS['grid']),
            yaxis=dict(gridcolor=self.COLORS['grid'])
        )
        
        return fig
    
    def create_humidity_temperature_scatter(self, cities: List[str] = None,
                                           time_aggregation: str = "Daily") -> go.Figure:
        """Create scatter plot for humidity vs temperature correlation"""
        df_filtered = self.df.copy()
        
        if cities:
            df_filtered = df_filtered[df_filtered['city'].isin(cities)]
        
        # Apply time aggregation
        if time_aggregation == "Weekly":
            df_filtered = df_filtered.groupby(['city', pd.Grouper(key='date', freq='W')]).agg({
                'temperature': 'mean',
                'humidity': 'mean', 
                'rainfall': 'sum'
            }).reset_index()
        elif time_aggregation == "Monthly":
            df_filtered = df_filtered.groupby(['city', pd.Grouper(key='date', freq='M')]).agg({
                'temperature': 'mean',
                'humidity': 'mean',
                'rainfall': 'sum'
            }).reset_index()
        
        fig = px.scatter(
            df_filtered,
            x='temperature',
            y='humidity',
            color='city',
            size='rainfall',
            title='Humidity vs Temperature (Bubble size = Rainfall)',
            labels={'temperature': 'Temperature (°C)', 'humidity': 'Humidity (%)'},
            hover_data=['date', 'rainfall'],
            color_discrete_sequence=self.CITY_COLORS
        )
        
        fig.update_layout(
            xaxis_title="Temperature (°C)",
            yaxis_title="Humidity (%)",
            legend_title="City",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color=self.COLORS['text'],
            xaxis=dict(gridcolor=self.COLORS['grid']),
            yaxis=dict(gridcolor=self.COLORS['grid'])
        )
        
        return fig
    
    def create_comprehensive_dashboard(self, cities: List[str] = None) -> go.Figure:
        """Create a comprehensive dashboard with multiple subplots"""
        df_filtered = self.df.copy()
        
        if cities:
            df_filtered = df_filtered[df_filtered['city'].isin(cities)]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Temperature Over Time',
                'Average Temperature by City',
                'Humidity vs Temperature',
                'Monthly Rainfall'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Temperature line chart
        for city in df_filtered['city'].unique():
            city_data = df_filtered[df_filtered['city'] == city]
            fig.add_trace(
                go.Scatter(
                    x=city_data['date'],
                    y=city_data['temperature'],
                    name=f'{city} Temp',
                    mode='lines'
                ),
                row=1, col=1
            )
        
        # Average temperature by city
        avg_temp = df_filtered.groupby('city')['temperature'].mean()
        fig.add_trace(
            go.Bar(
                x=avg_temp.index,
                y=avg_temp.values,
                name='Avg Temperature',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # Humidity vs Temperature scatter
        for city in df_filtered['city'].unique():
            city_data = df_filtered[df_filtered['city'] == city]
            fig.add_trace(
                go.Scatter(
                    x=city_data['temperature'],
                    y=city_data['humidity'],
                    mode='markers',
                    name=f'{city} H-T',
                    marker=dict(size=8)
                ),
                row=2, col=1
            )
        
        # Monthly rainfall
        monthly_rainfall = df_filtered.groupby(['month_year', 'city'])['rainfall'].sum().reset_index()
        for city in monthly_rainfall['city'].unique():
            city_data = monthly_rainfall[monthly_rainfall['city'] == city]
            fig.add_trace(
                go.Bar(
                    x=city_data['month_year'].astype(str),
                    y=city_data['rainfall'],
                    name=f'{city} Rain',
                    showlegend=False
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text="Weather Data Dashboard",
            showlegend=True
        )
        
        return fig
    
    def export_processed_data(self, filename: str = 'processed_weather_data.csv'):
        """Export processed data with additional columns"""
        export_df = self.df.copy()
        
        # Add additional calculated columns
        export_df['temperature_category'] = pd.cut(
            export_df['temperature'], 
            bins=[-np.inf, 10, 20, 30, np.inf], 
            labels=['Cold', 'Cool', 'Warm', 'Hot']
        )
        
        export_df['humidity_category'] = pd.cut(
            export_df['humidity'], 
            bins=[0, 30, 60, 80, 100], 
            labels=['Low', 'Moderate', 'High', 'Very High']
        )
        
        export_df['rainfall_category'] = pd.cut(
            export_df['rainfall'], 
            bins=[-0.1, 0, 2, 10, np.inf], 
            labels=['None', 'Light', 'Moderate', 'Heavy']
        )
        
        export_df.to_csv(filename, index=False)
        print(f"Processed data exported to {filename}")
        return export_df
    
    def print_summary_report(self):
        """Print a comprehensive summary report"""
        stats = self.calculate_summary_statistics()
        
        print("=" * 60)
        print("WEATHER DATA ANALYSIS SUMMARY REPORT")
        print("=" * 60)
        
        print(f"\nDataset Overview:")
        print(f"Total records: {len(self.df):,}")
        print(f"Date range: {self.df['date'].min().date()} to {self.df['date'].max().date()}")
        print(f"Cities analyzed: {', '.join(self.df['city'].unique())}")
        
        print(f"\nTemperature Analysis:")
        print(f"Overall average: {stats['temp_stats']['overall_avg']}°C")
        print(f"Highest recorded: {stats['temp_stats']['overall_max']}°C")
        print(f"Lowest recorded: {stats['temp_stats']['overall_min']}°C")
        
        print(f"\nAverage Temperature by City:")
        for city, temp in stats['avg_temp_by_city'].items():
            print(f"{city}: {temp}°C")
        
        print(f"\nHumidity Analysis:")
        print(f"Average humidity: {stats['humidity_stats']['avg_humidity']}%")
        max_humid = stats['humidity_stats']['max_humidity']
        min_humid = stats['humidity_stats']['min_humidity']
        print(f"Highest: {max_humid['humidity']}% ({max_humid['city']} on {max_humid['date'].date()})")
        print(f"Lowest: {min_humid['humidity']}% ({min_humid['city']} on {min_humid['date'].date()})")
        
        print(f"\nRainfall by Month:")
        for month, rainfall in stats['rainfall_by_month'].items():
            print(f"{month}: {rainfall:.1f}mm")
        
        print("=" * 60)