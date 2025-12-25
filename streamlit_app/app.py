"""
⚡ EVChargeAdvisor-AI - Premium Global Edition
==============================================

AI-Enhanced EV Charging Infrastructure Equity Analysis System
Works globally - Any country, any city!

Author: MAHBUB
Institution: Chulalongkorn University
Date: December 25, 2024
"""

import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.data_access.openchargemap import OpenChargeMapClient
from src.data_access.weather_api import WeatherAPIClient
from src.data_access.groq_api import GroqAPIClient
from src.analysis.infrastructure_analyzer import InfrastructureAnalyzer
from src.analysis.global_equity_analyzer import GlobalEquityAnalyzer
from src.analysis.accessibility_analyzer import AccessibilityAnalyzer
from src.visualization.map_visualizer import MapVisualizer
from src.visualization.chart_generator import ChartGenerator
from config.settings import PROJECT_NAME, VERSION, AUTHOR

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=f"{PROJECT_NAME} - Global Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# PREMIUM DARK THEME CSS
# =============================================================================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    
    /* Global Dark Theme */
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #111827 50%, #0f172a 100%);
    }
    
    /* Main container */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #f1f5f9 !important;
    }
    
    p, span, div, label {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Premium Header */
    .premium-header {
        background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 50%, #ec4899 100%);
        padding: 2.5rem 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(14, 165, 233, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.5;
    }
    
    .premium-header h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: white !important;
        margin: 0 !important;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .premium-header p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.2rem;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .premium-header .global-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-size: 0.9rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
        position: relative;
        z-index: 1;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(14, 165, 233, 0.2);
        border-color: #0ea5e9;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0ea5e9, #8b5cf6);
    }
    
    .metric-card .icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card .label {
        color: #94a3b8;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }
    
    .metric-card .delta {
        font-size: 0.85rem;
        color: #10b981;
        margin-top: 0.25rem;
    }
    
    /* Score Cards */
    .score-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
    }
    
    .score-card .grade {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 4rem;
        font-weight: 700;
        display: inline-block;
        width: 100px;
        height: 100px;
        line-height: 100px;
        border-radius: 50%;
        margin-bottom: 1rem;
    }
    
    .grade-a { background: linear-gradient(135deg, #10b981, #059669); color: white; }
    .grade-b { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; }
    .grade-c { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
    .grade-d { background: linear-gradient(135deg, #f97316, #ea580c); color: white; }
    .grade-f { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; }
    
    .score-card .score-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        color: #f1f5f9;
    }
    
    .score-card .score-label {
        color: #94a3b8;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(145deg, #1e3a5f 0%, #1e293b 100%);
        border: 1px solid #0ea5e9;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .info-box.success {
        border-color: #10b981;
        background: linear-gradient(145deg, #064e3b 0%, #1e293b 100%);
    }
    
    .info-box.warning {
        border-color: #f59e0b;
        background: linear-gradient(145deg, #78350f 0%, #1e293b 100%);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Sidebar header */
    .sidebar-header {
        text-align: center;
        padding: 1.5rem 1rem;
        border-bottom: 1px solid #334155;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-header h2 {
        font-size: 1.5rem !important;
        margin: 0 !important;
        background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sidebar-header .version {
        color: #64748b;
        font-size: 0.8rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #1e293b;
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #94a3b8;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9, #8b5cf6) !important;
        color: white !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #0ea5e9, #8b5cf6) !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #f1f5f9 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: #1e293b !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Footer */
    .premium-footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #334155;
        color: #64748b;
    }
    
    .premium-footer a {
        color: #0ea5e9;
        text-decoration: none;
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Country flag */
    .country-flag {
        font-size: 2rem;
        margin-right: 0.5rem;
    }
    
    /* Global indicator */
    .global-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #059669, #10b981);
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "infrastructure_analysis" not in st.session_state:
    st.session_state.infrastructure_analysis = None
if "equity_analysis" not in st.session_state:
    st.session_state.equity_analysis = None
if "accessibility_analysis" not in st.session_state:
    st.session_state.accessibility_analysis = None

# =============================================================================
# GLOBAL LOCATIONS DATABASE
# =============================================================================

GLOBAL_LOCATIONS = {
    "🇺🇸 San Francisco, USA": {
        "lat": 37.7749, "lon": -122.4194, 
        "country": "USA", "state_fips": "06", "county_fips": "075"
    },
    "🇺🇸 New York, USA": {
        "lat": 40.7128, "lon": -74.0060,
        "country": "USA", "state_fips": "36", "county_fips": "061"
    },
    "🇺🇸 Los Angeles, USA": {
        "lat": 34.0522, "lon": -118.2437,
        "country": "USA", "state_fips": "06", "county_fips": "037"
    },
    "🇬🇧 London, UK": {
        "lat": 51.5074, "lon": -0.1278,
        "country": "GBR", "state_fips": None, "county_fips": None
    },
    "🇩🇪 Berlin, Germany": {
        "lat": 52.5200, "lon": 13.4050,
        "country": "DEU", "state_fips": None, "county_fips": None
    },
    "🇫🇷 Paris, France": {
        "lat": 48.8566, "lon": 2.3522,
        "country": "FRA", "state_fips": None, "county_fips": None
    },
    "🇯🇵 Tokyo, Japan": {
        "lat": 35.6762, "lon": 139.6503,
        "country": "JPN", "state_fips": None, "county_fips": None
    },
    "🇨🇳 Shanghai, China": {
        "lat": 31.2304, "lon": 121.4737,
        "country": "CHN", "state_fips": None, "county_fips": None
    },
    "🇹🇭 Bangkok, Thailand": {
        "lat": 13.7563, "lon": 100.5018,
        "country": "THA", "state_fips": None, "county_fips": None
    },
    "🇸🇬 Singapore": {
        "lat": 1.3521, "lon": 103.8198,
        "country": "SGP", "state_fips": None, "county_fips": None
    },
    "🇦🇺 Sydney, Australia": {
        "lat": -33.8688, "lon": 151.2093,
        "country": "AUS", "state_fips": None, "county_fips": None
    },
    "🇮🇳 Mumbai, India": {
        "lat": 19.0760, "lon": 72.8777,
        "country": "IND", "state_fips": None, "county_fips": None
    },
    "🇧🇷 São Paulo, Brazil": {
        "lat": -23.5505, "lon": -46.6333,
        "country": "BRA", "state_fips": None, "county_fips": None
    },
    "🇿🇦 Cape Town, South Africa": {
        "lat": -33.9249, "lon": 18.4241,
        "country": "ZAF", "state_fips": None, "county_fips": None
    },
    "🌍 Custom Location": {
        "lat": None, "lon": None,
        "country": None, "state_fips": None, "county_fips": None
    }
}

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    # Header
    st.markdown("""
    <div class="sidebar-header">
        <h2>⚡ EVChargeAdvisor-AI</h2>
        <p class="version">v{} • Global Edition</p>
    </div>
    """.format(VERSION), unsafe_allow_html=True)
    
    # Global indicator
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <span class="global-indicator">🌍 Works Globally</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Location selection
    st.markdown("### 📍 Location")
    
    selected_location = st.selectbox(
        "Select City",
        options=list(GLOBAL_LOCATIONS.keys()),
        index=0,
        label_visibility="collapsed"
    )
    
    loc_data = GLOBAL_LOCATIONS[selected_location]
    
    # Custom location inputs
    if "Custom" in selected_location:
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=13.7563, format="%.4f")
        with col2:
            longitude = st.number_input("Longitude", value=100.5018, format="%.4f")
        
        country_code = st.text_input("Country Code (ISO 3)", value="THA", max_chars=3)
        
        # US-specific
        if country_code.upper() == "USA":
            col3, col4 = st.columns(2)
            with col3:
                state_fips = st.text_input("State FIPS", value="06")
            with col4:
                county_fips = st.text_input("County FIPS", value="075")
        else:
            state_fips = None
            county_fips = None
    else:
        latitude = loc_data["lat"]
        longitude = loc_data["lon"]
        country_code = loc_data["country"]
        state_fips = loc_data["state_fips"]
        county_fips = loc_data["county_fips"]
    
    # Search radius
    st.markdown("### 📏 Search Radius")
    radius_km = st.slider("Kilometers", 5, 50, 10, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Analyze button
    analyze_button = st.button("🔍 Analyze Location", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    # About
    st.markdown("### ℹ️ About")
    st.markdown(f"""
    <div style="font-size: 0.85rem; color: #94a3b8;">
    <b>EVChargeAdvisor-AI</b> provides AI-powered 
    analysis of EV charging infrastructure equity 
    and accessibility worldwide.
    <br><br>
    <b>Author:</b> {AUTHOR}<br>
    <b>Institution:</b> Chulalongkorn University
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN CONTENT
# =============================================================================

# Premium Header
location_display = selected_location.split(",")[0].replace("🇺🇸 ", "").replace("🇬🇧 ", "").replace("🇩🇪 ", "").replace("🇫🇷 ", "").replace("🇯🇵 ", "").replace("🇨🇳 ", "").replace("🇹🇭 ", "").replace("🇸🇬 ", "").replace("🇦🇺 ", "").replace("🇮🇳 ", "").replace("🇧🇷 ", "").replace("🇿🇦 ", "").replace("🌍 ", "")

st.markdown(f"""
<div class="premium-header">
    <h1>⚡ EVChargeAdvisor-AI</h1>
    <p>AI-Enhanced EV Charging Infrastructure Equity Analysis</p>
    <div class="global-badge">🌍 Global Coverage • 200+ Countries • Real-Time Data</div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# RUN ANALYSIS
# =============================================================================

if analyze_button:
    location_name = selected_location.replace("🇺🇸 ", "").replace("🇬🇧 ", "").replace("🇩🇪 ", "").replace("🇫🇷 ", "").replace("🇯🇵 ", "").replace("🇨🇳 ", "").replace("🇹🇭 ", "").replace("🇸🇬 ", "").replace("🇦🇺 ", "").replace("🇮🇳 ", "").replace("🇧🇷 ", "").replace("🇿🇦 ", "").replace("🌍 ", "")
    
    if "Custom" in selected_location:
        location_name = f"Custom ({latitude}, {longitude})"
    
    progress = st.progress(0)
    status = st.empty()
    
    try:
        # Initialize analyzers
        infra_analyzer = InfrastructureAnalyzer()
        equity_analyzer = GlobalEquityAnalyzer()
        access_analyzer = AccessibilityAnalyzer()
        
        # Step 1: Infrastructure
        status.info("🔌 Analyzing charging infrastructure...")
        progress.progress(10)
        
        infra_analysis = infra_analyzer.analyze_location(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            location_name=location_name
        )
        st.session_state.infrastructure_analysis = infra_analysis
        progress.progress(40)
        
        # Step 2: Equity (Global)
        status.info("🌍 Analyzing global equity metrics...")
        
        equity_analysis = equity_analyzer.analyze_equity(
            latitude=latitude,
            longitude=longitude,
            country_code=country_code,
            radius_km=radius_km,
            location_name=location_name,
            state_fips=state_fips,
            county_fips=county_fips
        )
        st.session_state.equity_analysis = equity_analysis
        progress.progress(70)
        
        # Step 3: Accessibility
        status.info("🏪 Analyzing accessibility...")
        
        access_analysis = access_analyzer.analyze_location_accessibility(
            latitude=latitude,
            longitude=longitude,
            radius_km=min(radius_km, 5),
            location_name=location_name,
            sample_size=8
        )
        st.session_state.accessibility_analysis = access_analysis
        progress.progress(100)
        
        st.session_state.analysis_complete = True
        status.success("✅ Analysis complete!")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        progress.empty()
        status.empty()

# =============================================================================
# DISPLAY RESULTS
# =============================================================================

if st.session_state.analysis_complete:
    infra = st.session_state.infrastructure_analysis
    equity = st.session_state.equity_analysis
    access = st.session_state.accessibility_analysis
    
    chart_gen = ChartGenerator()
    map_viz = MapVisualizer()
    
# Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📊 Overview",
        "🗺️ Map",
        "⚖️ Equity",
        "🏪 Accessibility",
        "🤖 AI Chat",
        "📄 Export",
        "🔄 Compare",
        "🔍 Stations",
        "🎯 Gap Finder",
        "💰 Cost Calculator"
    ])
    # =========================================================================
    # TAB 1: OVERVIEW
    # =========================================================================
    with tab1:
        st.markdown(f"## 📍 {infra['location']['name']}")
        
        # Data source badge
        data_source = equity.get("data_source", "N/A") if equity else "N/A"
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <span class="global-indicator">📡 Data: {data_source}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Metric cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">🔌</div>
                <div class="value">{infra['summary']['total_stations']:,}</div>
                <div class="label">Charging Stations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">🔋</div>
                <div class="value">{infra['summary']['total_connectors']:,}</div>
                <div class="label">Total Connectors</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">⚡</div>
                <div class="value">{infra['summary']['fast_chargers']:,}</div>
                <div class="label">Fast Chargers</div>
                <div class="delta">↑ {infra['summary']['fast_charger_ratio']}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">🏢</div>
                <div class="value">{infra['summary']['unique_operators']}</div>
                <div class="label">Operators</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Score cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            coverage = infra['coverage']
            st.markdown(f"""
            <div class="score-card">
                <div class="grade grade-{coverage['coverage_rating'][0].lower()}">{coverage['coverage_score']}</div>
                <div class="score-value">{coverage['coverage_rating']}</div>
                <div class="score-label">Coverage Rating</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if equity and equity.get("status") == "success":
                eq = equity['equity_assessment']
                st.markdown(f"""
                <div class="score-card">
                    <div class="grade grade-{eq['grade'].lower()}">{eq['grade']}</div>
                    <div class="score-value">{eq['score']}/100</div>
                    <div class="score-label">Equity Score</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Equity data not available")
        
        with col3:
            if access and access.get("status") == "success":
                acc = access['summary']
                grade = acc['overall_grade']
                st.markdown(f"""
                <div class="score-card">
                    <div class="grade grade-{grade.lower()}">{grade}</div>
                    <div class="score-value">{acc['avg_convenience_score']}/10</div>
                    <div class="score-label">Accessibility</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Accessibility data not available")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏢 Top Operators")
            op_chart = chart_gen.create_operator_bar_chart(infra['operators']['distribution'])
            st.plotly_chart(op_chart, use_container_width=True)
        
        with col2:
            st.markdown("### ⚡ Charging Levels")
            level_chart = chart_gen.create_charging_level_chart(infra['charging_levels'])
            st.plotly_chart(level_chart, use_container_width=True)
    
    # =========================================================================
    # TAB 2: MAP
    # =========================================================================
    with tab2:
        st.markdown("## 🗺️ Infrastructure Map")
        
        map_type = st.radio(
            "View",
            ["📍 Stations", "🔥 Heatmap", "🏢 By Operator", "📡 Coverage"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        stations = infra.get("stations", [])
        center = (latitude, longitude)
        
        if map_type == "📍 Stations":
            m = map_viz.create_cluster_map(stations, center=center)
        elif map_type == "🔥 Heatmap":
            m = map_viz.create_heatmap(stations, center=center)
        elif map_type == "🏢 By Operator":
            m = map_viz.create_operator_map(stations, center=center)
        else:
            m = map_viz.create_coverage_map(stations, coverage_radius_km=1, center=center)
        
        from streamlit_folium import st_folium
        st_folium(m, width=1200, height=600, returned_objects=[])
        
        st.caption(f"Showing {len(stations)} charging stations within {radius_km}km")
    
    # =========================================================================
    # TAB 3: EQUITY
    # =========================================================================
    with tab3:
        st.markdown("## ⚖️ Global Equity Analysis")
        
        if equity and equity.get("status") == "success":
            demo = equity.get("demographics", {})
            eq = equity.get("equity_assessment", {})
            
            # Demographics
            st.markdown(f"### 👥 Demographics ({equity.get('data_source', 'N/A')})")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                pop = demo.get("population", 0)
                st.metric("Population", f"{pop:,}" if pop else "N/A")
            with col2:
                income = demo.get("income_per_capita", 0)
                st.metric("Income/Capita", f"${income:,.0f}" if income else "N/A")
            with col3:
                poverty = demo.get("poverty_rate")
                st.metric("Poverty Rate", f"{poverty}%" if poverty else "N/A")
            with col4:
                level = demo.get("income_level", "N/A")
                st.metric("Income Level", level)
            
            st.markdown("---")
            
            # Equity visualization
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Equity Score")
                gauge = chart_gen.create_equity_gauge(eq['score'])
                st.plotly_chart(gauge, use_container_width=True)
            
            with col2:
                st.markdown("### 📈 Component Scores")
                radar = chart_gen.create_equity_components_chart(eq['components'])
                st.plotly_chart(radar, use_container_width=True)
            
            # Recommendations
            st.markdown("### 💡 Recommendations")
            for i, rec in enumerate(equity.get("recommendations", [])[:5], 1):
                with st.expander(f"{i}. [{rec['priority']}] {rec['category']}"):
                    st.write(f"**Recommendation:** {rec['recommendation']}")
                    st.write(f"**Rationale:** {rec['rationale']}")
        else:
            st.warning("Equity analysis not available for this location.")
    
    # =========================================================================
    # TAB 4: ACCESSIBILITY
    # =========================================================================
    with tab4:
        st.markdown("## 🏪 Accessibility Analysis")
        
        if access and access.get("status") == "success":
            summary = access['summary']
            climate = access.get("climate_impact", {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg Score", f"{summary['avg_convenience_score']}/10")
            with col2:
                st.metric("Overall Grade", summary['overall_grade'])
            with col3:
                ev_range = climate.get("current", {}).get("range_percentage", "N/A")
                st.metric("EV Range", ev_range)
            with col4:
                impact = climate.get("impact", {}).get("level", "N/A")
                st.metric("Climate Impact", impact)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Grade Distribution")
                grade_chart = chart_gen.create_grade_distribution_chart(access['grade_distribution'])
                st.plotly_chart(grade_chart, use_container_width=True)
            
            with col2:
                st.markdown("### 🏆 Top Accessible Stations")
                for station in access.get("top_stations", [])[:5]:
                    st.success(f"**{station['name']}** - {station['score']}/10 ({station['grade']})")
        else:
            st.warning("Accessibility data not available.")
    
    # =========================================================================
    # TAB 5: AI INSIGHTS
    # =========================================================================
    with tab5:
        st.markdown("## 🤖 AI-Powered Insights")
        
        if st.button("🔄 Generate AI Analysis", type="primary"):
            with st.spinner("🤖 AI is analyzing your data..."):
                try:
                    infra_analyzer = InfrastructureAnalyzer()
                    equity_analyzer = GlobalEquityAnalyzer()
                    
                    st.markdown("### 🔌 Infrastructure Insights")
                    infra_insights = infra_analyzer.generate_ai_insights(infra)
                    st.markdown(infra_insights)
                    
                    st.markdown("---")
                    
                    if equity and equity.get("status") == "success":
                        st.markdown("### ⚖️ Equity Insights")
                        equity_insights = equity_analyzer.generate_ai_insights(equity)
                        st.markdown(equity_insights)
                except Exception as e:
                    st.error(f"AI generation failed: {e}")
        else:
            st.info("Click the button to generate AI-powered insights for this location.")
# =========================================================================
    # TAB 6: EXPORT REPORTS
    # =========================================================================
    with tab6:
        st.markdown("## 📄 Export Reports")
        st.markdown("*Download professional reports of your analysis*")
        
        st.markdown("### 📋 Report Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_infra = st.checkbox("Include Infrastructure Analysis", value=True)
            include_equity = st.checkbox("Include Equity Analysis", value=True)
        
        with col2:
            include_access = st.checkbox("Include Accessibility Analysis", value=True)
            include_recommendations = st.checkbox("Include Recommendations", value=True)
        
        st.markdown("---")
        
        # Generate report function
        def generate_text_report():
            from datetime import datetime
            lines = []
            lines.append("=" * 80)
            lines.append(f"EVChargeAdvisor-AI - ANALYSIS REPORT")
            lines.append("=" * 80)
            lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Location: {infra['location']['name']}")
            lines.append("")
            
            if include_infra:
                lines.append("-" * 80)
                lines.append("INFRASTRUCTURE ANALYSIS")
                lines.append("-" * 80)
                lines.append(f"Total Stations: {infra['summary']['total_stations']}")
                lines.append(f"Total Connectors: {infra['summary']['total_connectors']}")
                lines.append(f"Fast Chargers: {infra['summary']['fast_chargers']}")
                lines.append(f"Operators: {infra['summary']['unique_operators']}")
                lines.append(f"Coverage: {infra['coverage']['coverage_rating']}")
                lines.append("")
            
            if include_equity and equity and equity.get("status") == "success":
                lines.append("-" * 80)
                lines.append("EQUITY ANALYSIS")
                lines.append("-" * 80)
                lines.append(f"Data Source: {equity.get('data_source', 'N/A')}")
                lines.append(f"Equity Score: {equity['equity_assessment']['score']}/100")
                lines.append(f"Grade: {equity['equity_assessment']['grade']}")
                demo = equity.get('demographics', {})
                lines.append(f"Population: {demo.get('population', 'N/A'):,}")
                lines.append(f"Income Level: {demo.get('income_level', 'N/A')}")
                lines.append("")
            
            if include_access and access and access.get("status") == "success":
                lines.append("-" * 80)
                lines.append("ACCESSIBILITY ANALYSIS")
                lines.append("-" * 80)
                lines.append(f"Convenience Score: {access['summary']['avg_convenience_score']}/10")
                lines.append(f"Grade: {access['summary']['overall_grade']}")
                lines.append("")
            
            if include_recommendations and equity:
                recs = equity.get("recommendations", [])
                if recs:
                    lines.append("-" * 80)
                    lines.append("RECOMMENDATIONS")
                    lines.append("-" * 80)
                    for i, rec in enumerate(recs, 1):
                        lines.append(f"{i}. [{rec['priority']}] {rec['recommendation']}")
                    lines.append("")
            
            lines.append("=" * 80)
            lines.append("END OF REPORT")
            
            return "\n".join(lines)
        
        # Download buttons
        col1, col2, col3 = st.columns(3)
        
        from datetime import datetime
        
        with col1:
            report_text = generate_text_report()
            st.download_button(
                label="📄 Download Text Report",
                data=report_text,
                file_name=f"evchargeadvisor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # CSV data
            csv_lines = ["Category,Metric,Value"]
            csv_lines.append(f"Infrastructure,Total Stations,{infra['summary']['total_stations']}")
            csv_lines.append(f"Infrastructure,Connectors,{infra['summary']['total_connectors']}")
            csv_lines.append(f"Infrastructure,Fast Chargers,{infra['summary']['fast_chargers']}")
            if equity and equity.get("status") == "success":
                csv_lines.append(f"Equity,Score,{equity['equity_assessment']['score']}")
                csv_lines.append(f"Equity,Grade,{equity['equity_assessment']['grade']}")
            
            st.download_button(
                label="📊 Download CSV Data",
                data="\n".join(csv_lines),
                file_name=f"evchargeadvisor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # JSON data
            import json
            json_data = {
                "location": infra['location'],
                "infrastructure": infra['summary'],
                "equity": equity.get('equity_assessment', {}) if equity else {},
                "accessibility": access.get('summary', {}) if access else {}
            }
            
            st.download_button(
                label="📋 Download JSON",
                data=json.dumps(json_data, indent=2),
                file_name=f"evchargeadvisor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Preview
        with st.expander("📖 Preview Text Report"):
            st.text(generate_text_report())
    
    # =========================================================================
    # TAB 7: COMPARE LOCATIONS
    # =========================================================================
    with tab7:
        st.markdown("## 🔄 Compare Locations")
        st.markdown("*Compare EV infrastructure across multiple cities*")
        
        st.info("🚧 **Coming Soon!** Multi-location comparison feature will allow you to compare infrastructure, equity, and accessibility across different cities worldwide.")
        
        # Placeholder comparison
        st.markdown("### 📊 Sample Global Comparison")
        
        import pandas as pd
        comparison_data = {
            "City": ["🇺🇸 San Francisco", "🇬🇧 London", "🇯🇵 Tokyo", "🇹🇭 Bangkok", "🇩🇪 Berlin"],
            "Stations": [435, 500, 380, 45, 320],
            "Equity Score": [90, 92, 85, 43, 88],
            "Grade": ["A", "A", "A", "D", "A"],
            "Data Source": ["US Census", "World Bank", "World Bank", "World Bank", "World Bank"]
        }
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Chart
        st.markdown("### 📈 Stations Comparison")
        chart_data = pd.DataFrame({
            "City": ["San Francisco", "London", "Tokyo", "Bangkok", "Berlin"],
            "Stations": [435, 500, 380, 45, 320]
        })
        st.bar_chart(chart_data.set_index("City"))
        
        st.markdown("---")
        st.markdown("*Full comparison feature with custom city selection coming in next update!*")
# =========================================================================
    # TAB 8: STATION FINDER
    # =========================================================================
    with tab8:
        st.markdown("## 🔍 Station Finder")
        st.markdown("*Search, filter, and explore charging stations*")
        
        stations = infra.get("stations", [])
        
        if not stations:
            st.warning("No station data available. Please run analysis first.")
        else:
            # Filters
            st.markdown("### 🎛️ Filters")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Get unique operators
            operators_list = list(set(
                s.get("operator", {}).get("name", "Unknown") 
                for s in stations
            ))
            operators_list.sort()
            
            with col1:
                search_query = st.text_input("🔎 Search by name", placeholder="Enter station name...")
            
            with col2:
                selected_operators = st.multiselect(
                    "🏢 Filter by Operator",
                    options=operators_list,
                    default=[]
                )
            
            with col3:
                min_power = st.slider("⚡ Minimum Power (kW)", 0, 350, 0)
            
            with col4:
                fast_only = st.checkbox("🚀 Fast Chargers Only (>50kW)")
            
            # Apply filters
            filtered_stations = stations.copy()
            
            if search_query:
                filtered_stations = [
                    s for s in filtered_stations 
                    if search_query.lower() in s.get("name", "").lower()
                ]
            
            if selected_operators:
                filtered_stations = [
                    s for s in filtered_stations 
                    if s.get("operator", {}).get("name") in selected_operators
                ]
            
            if min_power > 0:
                filtered_stations = [
                    s for s in filtered_stations 
                    if (s.get("total_power_kw") or 0) >= min_power
                ]
            
            if fast_only:
                filtered_stations = [
                    s for s in filtered_stations 
                    if any(c.get("power_kw", 0) > 50 for c in s.get("connections", []))
                ]
            
            st.markdown("---")
            
            # Results summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📍 Stations Found", len(filtered_stations))
            with col2:
                total_conn = sum(s.get("num_points", 0) for s in filtered_stations)
                st.metric("🔌 Total Connectors", total_conn)
            with col3:
                fast = sum(1 for s in filtered_stations 
                          for c in s.get("connections", []) 
                          if c.get("power_kw", 0) > 50)
                st.metric("⚡ Fast Chargers", fast)
            
            st.markdown("---")
            
            # Display stations
            st.markdown(f"### 📋 Results ({len(filtered_stations)} stations)")
            
            if filtered_stations:
                # Create dataframe for display
                import pandas as pd
                
                station_data = []
                for s in filtered_stations[:100]:  # Limit to 100 for performance
                    station_data.append({
                        "Name": s.get("name", "Unknown")[:40],
                        "Operator": s.get("operator", {}).get("name", "Unknown")[:20],
                        "Address": s.get("address", {}).get("line1", "N/A")[:30],
                        "City": s.get("address", {}).get("city", "N/A"),
                        "Connectors": s.get("num_points", 0),
                        "Power (kW)": s.get("total_power_kw", 0),
                        "Status": "✅" if s.get("status", {}).get("is_operational") else "❓"
                    })
                
                df = pd.DataFrame(station_data)
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Name": st.column_config.TextColumn("Station Name", width="large"),
                        "Power (kW)": st.column_config.NumberColumn("Power (kW)", format="%.1f"),
                        "Connectors": st.column_config.NumberColumn("🔌", width="small"),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    }
                )
                
                # Station details expander
                st.markdown("### 📍 Station Details")
                
                station_names = [s.get("name", "Unknown") for s in filtered_stations[:20]]
                selected_station_name = st.selectbox("Select a station for details", station_names)
                
                if selected_station_name:
                    selected_station = next(
                        (s for s in filtered_stations if s.get("name") == selected_station_name),
                        None
                    )
                    
                    if selected_station:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 📍 Location")
                            addr = selected_station.get("address", {})
                            st.write(f"**Address:** {addr.get('line1', 'N/A')}")
                            st.write(f"**City:** {addr.get('city', 'N/A')}, {addr.get('state', '')}")
                            st.write(f"**Postcode:** {addr.get('postcode', 'N/A')}")
                            
                            loc = selected_station.get("location", {})
                            st.write(f"**Coordinates:** ({loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')})")
                        
                        with col2:
                            st.markdown("#### 🔌 Connections")
                            for conn in selected_station.get("connections", []):
                                conn_type = conn.get("type", "Unknown")
                                power = conn.get("power_kw", 0)
                                qty = conn.get("quantity", 1)
                                fast = "⚡" if conn.get("is_fast_charge") else ""
                                st.write(f"• {conn_type}: **{power} kW** x{qty} {fast}")
                        
                        # Operator info
                        st.markdown("#### 🏢 Operator")
                        op = selected_station.get("operator", {})
                        st.write(f"**Name:** {op.get('name', 'Unknown')}")
                        if op.get("website"):
                            st.write(f"**Website:** {op.get('website')}")
            else:
                st.info("No stations match your filters. Try adjusting the criteria.")
# =========================================================================
    # TAB 9: GAP FINDER
    # =========================================================================
    with tab9:
        st.markdown("## 🎯 Infrastructure Gap Finder")
        st.markdown("*AI-powered analysis to identify optimal locations for new charging stations*")
        
        stations = infra.get("stations", [])
        
        # Current coverage summary
        st.markdown("### 📊 Current Coverage Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="icon">📍</div>
                <div class="value">{}</div>
                <div class="label">Current Stations</div>
            </div>
            """.format(infra['summary']['total_stations']), unsafe_allow_html=True)
        
        with col2:
            density = infra['coverage']['station_density']
            st.markdown("""
            <div class="metric-card">
                <div class="icon">📏</div>
                <div class="value">{:.2f}</div>
                <div class="label">Stations/km²</div>
            </div>
            """.format(density), unsafe_allow_html=True)
        
        with col3:
            fast_ratio = infra['summary']['fast_charger_ratio']
            st.markdown("""
            <div class="metric-card">
                <div class="icon">⚡</div>
                <div class="value">{}%</div>
                <div class="label">Fast Charger Ratio</div>
            </div>
            """.format(fast_ratio), unsafe_allow_html=True)
        
        with col4:
            coverage_rating = infra['coverage']['coverage_rating']
            st.markdown("""
            <div class="metric-card">
                <div class="icon">🎯</div>
                <div class="value">{}</div>
                <div class="label">Coverage Rating</div>
            </div>
            """.format(coverage_rating), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Gap Analysis
        st.markdown("### 🔍 Identified Gaps")
        
        gaps = infra.get("gaps", {})
        gap_list = gaps.get("gaps", [])
        
        if gap_list:
            for gap in gap_list:
                severity = gap.get("severity", "medium")
                if severity == "high":
                    st.error(f"🔴 **{gap.get('type', 'Unknown').replace('_', ' ').title()}**: {gap.get('description', 'N/A')}")
                elif severity == "medium":
                    st.warning(f"🟡 **{gap.get('type', 'Unknown').replace('_', ' ').title()}**: {gap.get('description', 'N/A')}")
                else:
                    st.info(f"🔵 **{gap.get('type', 'Unknown').replace('_', ' ').title()}**: {gap.get('description', 'N/A')}")
        else:
            st.success("✅ No significant infrastructure gaps identified!")
        
        st.markdown("---")
        
        # AI Gap Analysis
        st.markdown("### 🤖 AI Gap Analysis")
        
        if st.button("🎯 Generate AI Gap Analysis", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is analyzing infrastructure gaps..."):
                llm = GroqAPIClient()
                
                prompt = f"""Analyze EV charging infrastructure gaps for {infra['location']['name']}:

CURRENT INFRASTRUCTURE:
- Total Stations: {infra['summary']['total_stations']}
- Total Connectors: {infra['summary']['total_connectors']}
- Fast Chargers: {infra['summary']['fast_chargers']} ({infra['summary']['fast_charger_ratio']}%)
- Operators: {infra['summary']['unique_operators']}
- Coverage Rating: {infra['coverage']['coverage_rating']}
- Station Density: {infra['coverage']['station_density']:.2f} per km²

OPERATOR DISTRIBUTION:
{', '.join([f"{k}: {v.get('stations', v) if isinstance(v, dict) else v}" for k, v in list(infra['operators']['distribution'].items())[:5]])}

Provide:
1. **Critical Gaps**: What's missing or inadequate?
2. **Recommended Locations**: Where should new stations be built? (Be specific about area types)
3. **Priority Infrastructure**: What type of chargers are most needed?
4. **Quick Wins**: Low-cost improvements that would have high impact
5. **Long-term Strategy**: 3-5 year infrastructure development plan

Be specific and actionable."""

                response = llm.generate(
                    prompt=prompt,
                    system_prompt="You are an expert EV infrastructure planner. Provide detailed, actionable gap analysis.",
                    temperature=0.6,
                    max_tokens=1500
                )
                
                st.markdown(response)
        
        st.markdown("---")
        
        # Recommendations
        st.markdown("### 💡 Quick Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="info-box">
                <h4 style="color: #f1f5f9; margin-top: 0;">🏢 Commercial Areas</h4>
                <p style="color: #94a3b8;">Install fast chargers at shopping centers, office parks, and business districts where vehicles park for 1-4 hours.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
                <h4 style="color: #f1f5f9; margin-top: 0;">🏠 Residential Areas</h4>
                <p style="color: #94a3b8;">Deploy Level 2 chargers in apartment complexes and neighborhoods without home charging access.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
                <h4 style="color: #f1f5f9; margin-top: 0;">🛣️ Highway Corridors</h4>
                <p style="color: #94a3b8;">Install DC fast chargers every 50-80km along major highways for long-distance travel.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
                <h4 style="color: #f1f5f9; margin-top: 0;">🚌 Transit Hubs</h4>
                <p style="color: #94a3b8;">Place chargers at train stations, bus terminals, and park-and-ride facilities.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # =========================================================================
    # TAB 10: COST CALCULATOR
    # =========================================================================
    with tab10:
        st.markdown("## 💰 EV Charging Cost Calculator")
        st.markdown("*Estimate charging costs and compare with gasoline*")
        
        st.markdown("### ⚡ Charging Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            battery_capacity = st.number_input(
                "🔋 Battery Capacity (kWh)",
                min_value=20.0,
                max_value=200.0,
                value=60.0,
                step=5.0,
                help="Total battery capacity of your EV"
            )
            
            current_charge = st.slider(
                "📊 Current Charge Level (%)",
                min_value=0,
                max_value=100,
                value=20,
                help="Current battery percentage"
            )
        
        with col2:
            target_charge = st.slider(
                "🎯 Target Charge Level (%)",
                min_value=current_charge,
                max_value=100,
                value=80,
                help="Desired battery percentage"
            )
            
            charger_type = st.selectbox(
                "⚡ Charger Type",
                options=["Level 2 (7 kW)", "Level 2 (11 kW)", "Level 2 (22 kW)", 
                        "DC Fast (50 kW)", "DC Fast (150 kW)", "DC Fast (350 kW)"],
                index=3
            )
        
        with col3:
            electricity_rate = st.number_input(
                "💵 Electricity Rate ($/kWh)",
                min_value=0.05,
                max_value=1.00,
                value=0.15,
                step=0.01,
                help="Cost per kWh at the charging station"
            )
            
            charging_fee = st.number_input(
                "💳 Session Fee ($)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.50,
                help="Fixed fee per charging session"
            )
        
        st.markdown("---")
        
        # Calculate
        charger_power = {
            "Level 2 (7 kW)": 7,
            "Level 2 (11 kW)": 11,
            "Level 2 (22 kW)": 22,
            "DC Fast (50 kW)": 50,
            "DC Fast (150 kW)": 150,
            "DC Fast (350 kW)": 350
        }
        
        power = charger_power.get(charger_type, 50)
        energy_needed = battery_capacity * (target_charge - current_charge) / 100
        charging_time = energy_needed / power
        total_cost = (energy_needed * electricity_rate) + charging_fee
        cost_per_percent = total_cost / max(target_charge - current_charge, 1)
        
        # Results
        st.markdown("### 📊 Charging Estimate")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">⚡</div>
                <div class="value">{energy_needed:.1f}</div>
                <div class="label">kWh Needed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            hours = int(charging_time)
            minutes = int((charging_time - hours) * 60)
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">⏱️</div>
                <div class="value">{time_str}</div>
                <div class="label">Charging Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">💵</div>
                <div class="value">${total_cost:.2f}</div>
                <div class="label">Total Cost</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="icon">📈</div>
                <div class="value">${cost_per_percent:.3f}</div>
                <div class="label">Cost per %</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Comparison with gasoline
        st.markdown("### ⛽ vs Gasoline Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ev_efficiency = st.number_input(
                "🚗 EV Efficiency (miles/kWh)",
                min_value=2.0,
                max_value=6.0,
                value=3.5,
                step=0.1
            )
            
            gas_price = st.number_input(
                "⛽ Gas Price ($/gallon)",
                min_value=1.0,
                max_value=10.0,
                value=3.50,
                step=0.10
            )
        
        with col2:
            gas_mpg = st.number_input(
                "🚙 Gas Car MPG",
                min_value=15.0,
                max_value=60.0,
                value=30.0,
                step=1.0
            )
        
        # Calculate comparison
        ev_range_added = energy_needed * ev_efficiency
        ev_cost_per_mile = total_cost / max(ev_range_added, 1)
        
        gas_gallons_equivalent = ev_range_added / gas_mpg
        gas_cost_equivalent = gas_gallons_equivalent * gas_price
        gas_cost_per_mile = gas_price / gas_mpg
        
        savings = gas_cost_equivalent - total_cost
        savings_percent = (savings / max(gas_cost_equivalent, 0.01)) * 100
        
        st.markdown("### 📊 Cost Comparison")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #10b981;">
                <div class="icon">⚡</div>
                <div class="value" style="color: #10b981;">${total_cost:.2f}</div>
                <div class="label">EV Charging Cost</div>
                <div class="delta">${ev_cost_per_mile:.3f}/mile</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #f59e0b;">
                <div class="icon">⛽</div>
                <div class="value" style="color: #f59e0b;">${gas_cost_equivalent:.2f}</div>
                <div class="label">Gas Equivalent Cost</div>
                <div class="delta">${gas_cost_per_mile:.3f}/mile</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            savings_color = "#10b981" if savings > 0 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {savings_color};">
                <div class="icon">💰</div>
                <div class="value" style="color: {savings_color};">${abs(savings):.2f}</div>
                <div class="label">{"Savings" if savings > 0 else "Extra Cost"}</div>
                <div class="delta">{savings_percent:.1f}% {"saved" if savings > 0 else "more"}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Range added
        st.markdown(f"""
        <div class="info-box success">
            <h4 style="color: #f1f5f9; margin: 0;">🛣️ Range Added: {ev_range_added:.0f} miles ({ev_range_added * 1.6:.0f} km)</h4>
            <p style="color: #94a3b8; margin: 0.5rem 0 0 0;">From {current_charge}% to {target_charge}% charge</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Annual savings estimate
        st.markdown("---")
        st.markdown("### 📅 Annual Savings Estimate")
        
        annual_miles = st.slider("Annual Driving (miles)", 5000, 30000, 12000, 1000)
        
        annual_ev_cost = (annual_miles / ev_efficiency) * electricity_rate
        annual_gas_cost = (annual_miles / gas_mpg) * gas_price
        annual_savings = annual_gas_cost - annual_ev_cost
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("⚡ Annual EV Cost", f"${annual_ev_cost:,.0f}")
        with col2:
            st.metric("⛽ Annual Gas Cost", f"${annual_gas_cost:,.0f}")
        with col3:
            st.metric("💰 Annual Savings", f"${annual_savings:,.0f}", delta=f"{(annual_savings/annual_gas_cost)*100:.0f}%")
else:
    # Welcome screen
    st.markdown("""
    <div class="info-box">
        <h3 style="color: #f1f5f9; margin-top: 0;">👋 Welcome to EVChargeAdvisor-AI Global Edition!</h3>
        <p style="color: #94a3b8;">
            Analyze EV charging infrastructure equity and accessibility for <b>any location worldwide</b>.
        </p>
        <p style="color: #94a3b8;"><b>Quick Start:</b></p>
        <ol style="color: #94a3b8;">
            <li>Select a city from the sidebar (14+ cities available)</li>
            <li>Or enter custom coordinates for any location</li>
            <li>Click <b>"🔍 Analyze Location"</b></li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Features
    st.markdown("### ✨ Premium Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🌍</div>
            <div class="label" style="font-size: 1.1rem; color: #f1f5f9;">Global Coverage</div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
                Works in 200+ countries with real-time data from OpenChargeMap
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🤖</div>
            <div class="label" style="font-size: 1.1rem; color: #f1f5f9;">AI-Powered</div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
                LLM-generated insights and policy recommendations
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">⚖️</div>
            <div class="label" style="font-size: 1.1rem; color: #f1f5f9;">Equity Focus</div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;">
                Demographic analysis using Census (USA) & World Bank (Global)
            </p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown(f"""
<div class="premium-footer">
    <p>⚡ <b>EVChargeAdvisor-AI</b> Global Edition v{VERSION}</p>
    <p>Built with ❤️ by {AUTHOR} • Chulalongkorn University</p>
    <p style="font-size: 0.8rem; margin-top: 1rem;">
        Powered by OpenChargeMap • US Census Bureau • World Bank • OpenStreetMap • Groq LLM
    </p>
</div>
""", unsafe_allow_html=True)