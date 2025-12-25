"""
⚙️ System Settings & Constants
==============================

Author: MAHBUB
Date: December 25, 2024
"""

# =============================================================================
# PROJECT INFORMATION
# =============================================================================

PROJECT_NAME = "EVChargeAdvisor-AI"
VERSION = "1.0.0"
AUTHOR = "MAHBUB"
INSTITUTION = "Chulalongkorn University"

# =============================================================================
# DEFAULT SEARCH PARAMETERS
# =============================================================================

DEFAULT_LOCATION = {
    "city": "San Francisco",
    "state": "California",
    "country": "US",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "radius_km": 10
}

# =============================================================================
# API SETTINGS
# =============================================================================

API_SETTINGS = {
    "timeout": 30,  # seconds
    "max_retries": 3,
    "retry_delay": 1,  # seconds
    "cache_duration": 3600,  # 1 hour in seconds
}

# OpenChargeMap settings
OPENCHARGE_SETTINGS = {
    "max_results": 500,
    "distance_unit": "km",
    "compact": False,
    "verbose": False
}

# Census API settings
CENSUS_SETTINGS = {
    "year": 2022,
    "dataset": "acs/acs5",
    "variables": [
        "B01003_001E",  # Total population
        "B19013_001E",  # Median household income
        "B17001_002E",  # Population below poverty
        "B25044_001E",  # Vehicles available
    ]
}

# Overpass API settings
OVERPASS_SETTINGS = {
    "timeout": 60,
    "amenity_types": [
        "restaurant",
        "cafe", 
        "fast_food",
        "bank",
        "pharmacy",
        "supermarket",
        "convenience"
    ],
    "transit_types": [
        "bus_stop",
        "subway_entrance",
        "train_station"
    ]
}

# Weather API settings
WEATHER_SETTINGS = {
    "forecast_days": 7,
    "temperature_unit": "celsius",
    "variables": [
        "temperature_2m",
        "precipitation",
        "weathercode"
    ]
}

# =============================================================================
# LLM SETTINGS
# =============================================================================

LLM_SETTINGS = {
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 0.9
}

# =============================================================================
# SCORING WEIGHTS
# =============================================================================

CONVENIENCE_WEIGHTS = {
    "restaurants": 2.0,
    "cafes": 1.5,
    "shopping": 1.5,
    "transit": 2.5,
    "services": 1.5,
    "healthcare": 1.0
}

EQUITY_WEIGHTS = {
    "income": 0.35,
    "poverty": 0.25,
    "vehicle_access": 0.20,
    "population_density": 0.20
}

# =============================================================================
# VISUALIZATION SETTINGS
# =============================================================================

MAP_SETTINGS = {
    "default_zoom": 12,
    "tile_provider": "CartoDB positron",
    "cluster_radius": 50
}

CHART_COLORS = {
    "primary": "#3b82f6",
    "secondary": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "info": "#06b6d4",
    "operators": {
        "ChargePoint": "#FF6B35",
        "Tesla": "#E82127",
        "EVgo": "#00A94F",
        "Electrify America": "#00264C",
        "Other": "#6B7280"
    }
}

# =============================================================================
# FILE PATHS
# =============================================================================

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATHS = {
    "data_raw": os.path.join(BASE_DIR, "data", "raw"),
    "data_processed": os.path.join(BASE_DIR, "data", "processed"),
    "data_cache": os.path.join(BASE_DIR, "data", "cache"),
    "data_exports": os.path.join(BASE_DIR, "data", "exports"),
    "logs": os.path.join(BASE_DIR, "logs"),
}

# Create directories if they don't exist
for path in PATHS.values():
    os.makedirs(path, exist_ok=True)

# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print(f"⚙️ {PROJECT_NAME} Settings")
    print("=" * 60)
    print(f"Version: {VERSION}")
    print(f"Author: {AUTHOR}")
    print(f"\nDefault Location: {DEFAULT_LOCATION['city']}")
    print(f"LLM Model: {LLM_SETTINGS['model']}")
    print("\n✅ All settings loaded!")