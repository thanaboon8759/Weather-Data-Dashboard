import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from weather_collector import WeatherDataCollector
from weather_analyzer import WeatherAnalyzer

# Page configuration
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ultra-Clean Minimal Weather Dashboard
st.markdown("""
<style>
    /* Hide all Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1d391kg {padding-top: 0.5rem;}
    
    /* Minimal color palette */
    :root {
        --white: #FFFFFF;
        --gray-50: #F9FAFB;
        --gray-100: #F3F4F6;
        --gray-200: #E5E7EB;
        --gray-500: #6B7280;
        --gray-900: #111827;
        --blue-500: #3B82F6;
        --emerald-500: #10B981;
        --orange-500: #F59E0B;
    }
    
    /* Ultra-clean global styles */
    .main .block-container {
        padding: 0rem 2rem 2rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
        background: var(--white);
    }
    
    .stApp {
        background: var(--gray-50);
    }
    
    /* Remove default Streamlit styling */
    .css-1v0mbdj img {
        border-radius: 8px;
    }
    
    /* Clean spacing and typography */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Minimal text styling */
    h1, h2, h3, h4, h5, h6 {
        color: var(--gray-900);
        font-weight: 300;
        letter-spacing: -0.025em;
    }
    
    p, div, span {
        color: var(--gray-500);
        line-height: 1.6;
    }
    
    /* Clean number displays */
    .metric-container {
        background: var(--white);
        border: 1px solid var(--gray-100);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }
    
    /* Ultra-minimal header */
    .clean-header {
        text-align: center;
        padding: 3rem 0 2rem 0;
        background: var(--white);
        color: var(--gray-900);
        margin-bottom: 3rem;
        border: 2px solid var(--gray-200);
        border-radius: 8px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .clean-header h1 {
        font-size: 2.5rem;
        font-weight: 300;
        margin: 0;
        letter-spacing: -0.025em;
        color: var(--gray-900);
    }
    
    .clean-header p {
        font-size: 1rem;
        margin: 0.75rem 0 0 0;
        color: var(--gray-500);
        font-weight: 400;
    }
    
    /* Ultra-clean cards with visible borders */
    .simple-card {
        background: var(--white);
        border-radius: 8px;
        padding: 2rem;
        border: 2px solid var(--gray-200);
        margin: 1.5rem 0;
        transition: border-color 0.2s ease;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .simple-card:hover {
        border-color: var(--gray-500);
        box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Minimal metric display */
    .metric-display {
        text-align: center;
        padding: 1rem 0;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 200;
        color: var(--gray-900);
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .metric-label {
        color: var(--gray-500);
        font-size: 0.875rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    /* Clean status indicators */
    .status-good {
        background: var(--gray-50);
        color: var(--emerald-500);
        padding: 1rem;
        border-radius: 6px;
        text-align: center;
        margin: 1rem 0;
        border: 1px solid var(--gray-100);
        font-weight: 500;
    }
    
    .status-warning {
        background: var(--gray-50);
        color: var(--orange-500);
        padding: 1rem;
        border-radius: 6px;
        text-align: center;
        margin: 1rem 0;
        border: 1px solid var(--gray-100);
        font-weight: 500;
    }
    
    /* Minimal section headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 400;
        color: var(--gray-900);
        margin: 2.5rem 0 1.5rem 0;
        letter-spacing: -0.015em;
    }
    
    /* Minimal footer with border */
    .clean-footer {
        background: var(--gray-50);
        border-radius: 6px;
        padding: 1.5rem;
        border: 2px solid var(--gray-200);
        margin-top: 3rem;
        text-align: center;
        color: var(--gray-500);
        font-size: 0.875rem;
    }
    
    /* Filter section borders */
    .filter-section {
        background: var(--gray-50);
        border: 2px solid var(--gray-200);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    /* Section dividers */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--gray-200), transparent);
        margin: 2rem 0;
        border-radius: 1px;
    }
    
    /* Clean tabs with visible borders */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--gray-50);
        border-radius: 8px;
        padding: 4px;
        margin-bottom: 2rem;
        border: 2px solid var(--gray-200);
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        color: var(--gray-500);
        font-weight: 400;
        padding: 12px 24px;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--white);
        color: var(--gray-900);
        border: 1px solid var(--gray-200);
        box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Clean button styling */
    .stButton > button {
        background: var(--white) !important;
        color: var(--gray-900) !important;
        border: 2px solid var(--gray-900) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
        font-size: 0.875rem !important;
    }
    
    .stButton > button:hover {
        background: var(--gray-50) !important;
        color: var(--gray-900) !important;
        border-color: var(--gray-900) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:focus {
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    /* Clean multiselect styling */
    .stMultiSelect [data-baseweb="tag"] {
        background: var(--white) !important;
        color: var(--gray-900) !important;
        border: 1px solid var(--gray-900) !important;
        border-radius: 4px !important;
        font-weight: 400 !important;
        margin: 2px !important;
        padding: 4px 8px !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] svg {
        color: var(--gray-900) !important;
    }
    
    .stMultiSelect [data-baseweb="tag"]:hover {
        background: var(--gray-50) !important;
        border-color: var(--gray-900) !important;
    }
    
    /* Clean multiselect dropdown */
    .stMultiSelect > div > div {
        border: 1px solid var(--gray-200) !important;
        border-radius: 6px !important;
    }
    
    .stMultiSelect > div > div:focus-within {
        border-color: var(--blue-500) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .clean-header h1 {
            font-size: 2rem;
        }
        .simple-card {
            padding: 1.5rem;
        }
        .main .block-container {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def load_or_generate_data():
    """Load existing data or generate new weather data"""
    data_file = 'weather_data.csv'
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        # Generate new data with API if available
        collector = WeatherDataCollector()
        cities = ['Bangkok', 'Tokyo', 'London', 'New York', 'Sydney', 'Mumbai']
        df = collector.collect_historical_data(cities, days=90)
        df.to_csv(data_file, index=False)
        return df

def get_current_weather_data():
    """Fetch current weather data from API"""
    collector = WeatherDataCollector()
    if collector.api_key:
        cities = ['Bangkok', 'Tokyo', 'London', 'New York', 'Sydney', 'Mumbai']
        return collector.collect_current_weather_all_cities(cities)
    return None

def main():
    # Clean modern header
    st.markdown("""
    <div class="clean-header">
        <h1>🌤️ Weather Dashboard</h1>
        <p>Clean Weather Analytics & Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple API status
    collector = WeatherDataCollector()
    
    if collector.api_key:
        st.markdown(f"""
        <div class="status-good">
            <strong>✅ API Connected</strong> • Key: {collector.api_key[:8]}...
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced refresh button
        if st.button("🔄 Fetch Live Weather Data", type="primary", use_container_width=True):
            with st.spinner("Fetching real-time weather data from API..."):
                current_data = get_current_weather_data()
                if current_data is not None and not current_data.empty:
                    st.success("✅ Live weather data updated successfully!")
                    
                    # Display current weather in a nice format
                    st.markdown("### 🌍 Current Weather Conditions")
                    
                    # Create metrics for current weather
                    cols = st.columns(len(current_data))
                    for idx, (_, row) in enumerate(current_data.iterrows()):
                        with cols[idx]:
                            st.metric(
                                label=f"🏙️ {row['city']}",
                                value=f"{row['temperature']:.1f}°C",
                                delta=f"💧 {row['humidity']:.0f}% humidity"
                            )
                            if row['rainfall'] > 0:
                                st.write(f"🌧️ {row['rainfall']:.1f}mm rain")
                            else:
                                st.write("☀️ No rain")
                else:
                    st.error("❌ Failed to fetch current weather data")
    else:
        st.markdown("""
        <div class="status-warning">
            <strong>⚠️ API Not Configured</strong> • Add OpenWeatherMap API key to .env file
        </div>
        """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading weather data..."):
        df = load_or_generate_data()
    
    # Clean overview section
    st.markdown('<div class="section-title">📊 Dataset Overview</div>', unsafe_allow_html=True)
    
    # Simple metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="simple-card">
            <div class="metric-display">
                <div class="metric-value">{:,}</div>
                <div class="metric-label">Total Records</div>
            </div>
        </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col2:
        cities_count = df['city'].nunique()
        st.markdown("""
        <div class="simple-card">
            <div class="metric-display">
                <div class="metric-value">{}</div>
                <div class="metric-label">Cities</div>
            </div>
        </div>
        """.format(cities_count), unsafe_allow_html=True)
    
    with col3:
        date_range = (df['date'].max() - df['date'].min()).days
        st.markdown("""
        <div class="simple-card">
            <div class="metric-display">
                <div class="metric-value">{}</div>
                <div class="metric-label">Days of Data</div>
            </div>
        </div>
        """.format(date_range), unsafe_allow_html=True)
    
    with col4:
        temp_avg = df['temperature'].mean()
        st.markdown("""
        <div class="simple-card">
            <div class="metric-display">
                <div class="metric-value">{:.1f}°C</div>
                <div class="metric-label">Avg Temperature</div>
            </div>
        </div>
        """.format(temp_avg), unsafe_allow_html=True)
    
    # Initialize analyzer with full dataset
    analyzer = WeatherAnalyzer(df)
    
    # Section divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Data Filtering Section
    st.markdown('<h2 class="section-header">🔍 Data Filters & Analysis</h2>', unsafe_allow_html=True)
    
    # Create filter columns for better layout
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
    
    with filter_col1:
        # City selection
        available_cities = df['city'].unique().tolist()
        selected_cities = st.multiselect(
            "Select Cities for Analysis:",
            available_cities,
            default=available_cities[:3],
            help="Choose which cities to include in the analysis"
        )
    
    with filter_col2:
        # Date range selection
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        
        date_range = st.date_input(
            "Select Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Filter data by date range"
        )
    
    with filter_col3:
        # Apply filters button for better UX
        apply_filters = st.button("Apply Filters", type="primary", use_container_width=True)
    
    # Filter data based on selections
    filtered_df = df.copy()
    
    if selected_cities:
        filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= start_date) & 
            (filtered_df['date'].dt.date <= end_date)
        ]
    
    # Update analyzer with filtered data
    if not filtered_df.empty:
        analyzer = WeatherAnalyzer(filtered_df)
        
        # Show filter results
        st.success(f"✅ Filtered data: {len(filtered_df):,} records from {len(selected_cities)} cities")
    else:
        st.warning("⚠️ No data available for selected filters. Please adjust your selection.")
        return
    
    # Enhanced Key Metrics Section
    st.markdown('<h3 class="section-header">📊 Key Metrics</h3>', unsafe_allow_html=True)
    
    stats = analyzer.calculate_summary_statistics()
    
    # Create enhanced metric cards
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        temp_delta = stats['temp_stats']['overall_max'] - stats['temp_stats']['overall_min']
        st.metric(
            "Average Temperature",
            f"{stats['temp_stats']['overall_avg']}°C",
            delta=f"Range: {temp_delta:.1f}°C",
            help=f"Min: {stats['temp_stats']['overall_min']}°C, Max: {stats['temp_stats']['overall_max']}°C"
        )
    
    with metric_col2:
        humidity_range = filtered_df['humidity'].max() - filtered_df['humidity'].min()
        st.metric(
            "Average Humidity",
            f"{stats['humidity_stats']['avg_humidity']}%",
            delta=f"Range: {humidity_range:.0f}%",
            help=f"Min: {filtered_df['humidity'].min():.0f}%, Max: {filtered_df['humidity'].max():.0f}%"
        )
    
    with metric_col3:
        total_rainfall = filtered_df['rainfall'].sum()
        rainy_days = (filtered_df['rainfall'] > 0).sum()
        st.metric(
            "Total Rainfall",
            f"{total_rainfall:.1f}mm",
            delta=f"Rainy days: {rainy_days}",
            help=f"Average per day: {total_rainfall/len(filtered_df):.2f}mm"
        )
    
    with metric_col4:
        date_span = (filtered_df['date'].max() - filtered_df['date'].min()).days
        st.metric(
            "Dataset Span",
            f"{date_span} days",
            delta=f"{len(selected_cities)} cities",
            help=f"Total records: {len(filtered_df):,}"
        )
    
    # Section divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Clean charts section
    st.markdown('<div class="section-title">📈 Weather Analytics</div>', unsafe_allow_html=True)
    
    # Chart control panel
    chart_col1, chart_col2, chart_col3 = st.columns([2, 2, 1])
    
    with chart_col1:
        chart_type = st.selectbox(
            "Chart Display Mode:",
            ["Interactive", "Static", "Both"],
            help="Choose how to display the charts"
        )
    
    with chart_col2:
        time_aggregation = st.selectbox(
            "Time Aggregation:",
            ["Daily", "Weekly", "Monthly"],
            help="How to group the time-series data"
        )
    
    with chart_col3:
        show_trend = st.checkbox("Show Trend Lines", value=True)
    
    # Simple chart tabs
    tab1, tab2, tab3 = st.tabs(["🌡️ Temperature", "💧 Rainfall & Humidity", "🏙️ City Analysis"])
    
    with tab1:
        if selected_cities and not filtered_df.empty:
            temp_chart = analyzer.create_temperature_line_chart(
                cities=selected_cities,
                time_aggregation=time_aggregation,
                show_trend=show_trend
            )
            
            if chart_type in ["Interactive", "Both"]:
                st.plotly_chart(temp_chart, use_container_width=True)
            
            if chart_type in ["Static", "Both"]:
                st.markdown("**Static View:**")
                fig_static = analyzer.create_static_temperature_chart(
                    cities=selected_cities,
                    time_aggregation=time_aggregation
                )
                st.pyplot(fig_static)
        else:
            st.info("📊 Select cities and ensure data is available to view temperature charts.")
    
    with tab2:
        if not filtered_df.empty:
            if chart_type in ["Interactive", "Both"]:
                rainfall_chart = analyzer.create_rainfall_bar_chart(time_aggregation=time_aggregation)
                st.plotly_chart(rainfall_chart, use_container_width=True)
            
            if chart_type in ["Static", "Both"]:
                if chart_type == "Both":
                    st.markdown("**Static View:**")
                static_rainfall = analyzer.create_static_rainfall_chart(time_aggregation=time_aggregation)
                st.pyplot(static_rainfall)
        else:
            st.info("📊 Ensure data is available to view rainfall charts.")

    
    with tab3:
        if selected_cities and not filtered_df.empty:
            if chart_type in ["Interactive", "Both"]:
                humidity_scatter = analyzer.create_humidity_temperature_scatter(
                    cities=selected_cities,
                    time_aggregation=time_aggregation
                )
                st.plotly_chart(humidity_scatter, use_container_width=True)
            
            if chart_type in ["Static", "Both"]:
                if chart_type == "Both":
                    st.markdown("**Static View:**")
                static_scatter = analyzer.create_static_humidity_scatter(
                    cities=selected_cities,
                    time_aggregation=time_aggregation
                )
                st.pyplot(static_scatter)
        else:
            st.info("📊 Select cities and ensure data is available to view scatter plots.")
        
        # Simple stats table
        if selected_cities and not filtered_df.empty:
            st.markdown("### 📈 City Statistics Summary")
            city_stats = filtered_df.groupby('city').agg({
                'temperature': 'mean',
                'humidity': 'mean',
                'rainfall': 'sum'
            }).round(1)
            st.dataframe(city_stats, use_container_width=True)
    
    # Clean footer
    st.markdown(f"""
    <div class="clean-footer">
        <p><strong>Weather Dashboard</strong> • Built with Streamlit & Plotly</p>
        <p>Real-time weather data • Interactive analytics • Multi-city insights</p>
        <p style="font-size: 0.8rem; margin-top: 1rem;">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()