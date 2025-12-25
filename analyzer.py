"""
EV Charging Equity Analyzer
============================

Combines charging station data with demographics and generates AI insights.

Author: MAHBUB
Date: December 25, 2024
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.data_access.openchargemap_client import OpenChargeMapClient
from src.data_access.census_client import CensusClient
from config.api_keys import GROQ_API_KEY
import requests


def analyze_location(city_name: str, latitude: float, longitude: float, state_fips: str, county_fips: str):
    """
    Analyze EV charging equity for a location.
    
    Args:
        city_name: City name
        latitude: City latitude
        longitude: City longitude
        state_fips: State FIPS code
        county_fips: County FIPS code
    """
    print("=" * 70)
    print(f"🚗⚡ EV CHARGING EQUITY ANALYSIS: {city_name}")
    print("=" * 70)
    
    # Step 1: Get charging stations
    print("\n📍 STEP 1: Getting Charging Stations...")
    print("-" * 70)
    
    ocm_client = OpenChargeMapClient()
    stations = ocm_client.get_stations_by_location(
        latitude=latitude,
        longitude=longitude,
        radius_km=10,
        max_results=50
    )
    
    num_stations = len(stations)
    print(f"✅ Found {num_stations} charging stations")
    
    # Step 2: Get demographics
    print("\n👥 STEP 2: Getting Demographics...")
    print("-" * 70)
    
    census_client = CensusClient()
    tracts = census_client.get_tract_demographics(
        state_fips=state_fips,
        county_fips=county_fips
    )
    
    demographics = census_client.calculate_summary(tracts)
    print(f"✅ Analyzed {demographics['num_tracts']} census tracts")
    
    # Step 3: Calculate metrics
    print("\n📊 STEP 3: Calculating Metrics...")
    print("-" * 70)
    
    population = demographics['total_population']
    avg_income = demographics['avg_median_income']
    poverty_rate = demographics['poverty_rate']
    
    stations_per_1000 = (num_stations / population * 1000) if population > 0 else 0
    
    print(f"Population: {population:,}")
    print(f"Avg Median Income: ${avg_income:,.0f}")
    print(f"Poverty Rate: {poverty_rate:.1f}%")
    print(f"Charging Stations: {num_stations}")
    print(f"Stations per 1,000 people: {stations_per_1000:.2f}")
    
    # Step 4: LLM Analysis
    print("\n🤖 STEP 4: Generating AI Insights...")
    print("-" * 70)
    
    prompt = f"""You are an urban planning expert analyzing EV charging infrastructure equity.

Location: {city_name}

INFRASTRUCTURE DATA:
- Total charging stations: {num_stations}
- Stations per 1,000 people: {stations_per_1000:.2f}

DEMOGRAPHIC DATA:
- Total population: {population:,}
- Average median income: ${avg_income:,.0f}
- Poverty rate: {poverty_rate:.1f}%

Provide a brief analysis (3-4 sentences):
1. Overall infrastructure assessment
2. Equity implications based on income and poverty data
3. One key recommendation

Be concise and actionable."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            insight = response.json()['choices'][0]['message']['content']
            print("\n💡 AI ANALYSIS:")
            print("-" * 70)
            print(insight)
        else:
            print(f"❌ LLM Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    # Analyze San Francisco
    analyze_location(
        city_name="San Francisco",
        latitude=37.7749,
        longitude=-122.4194,
        state_fips="06",
        county_fips="075"
    )