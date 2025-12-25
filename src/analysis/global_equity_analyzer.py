"""
🌍 Global Equity Analyzer
=========================

Analyzes equity in EV charging access for ANY country.
Uses US Census for USA, World Bank for all other countries.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.census_client import CensusAPIClient
from src.data_access.worldbank_api import WorldBankAPIClient
from src.data_access.openchargemap import OpenChargeMapClient
from src.data_access.groq_api import GroqAPIClient


class GlobalEquityAnalyzer:
    """
    Analyzes equity in EV charging infrastructure globally.
    
    Automatically selects data source:
    - USA: US Census Bureau (detailed county/tract data)
    - Other countries: World Bank (country-level data)
    """
    
    def __init__(self):
        """Initialize analyzer with API clients."""
        self.census_client = CensusAPIClient()
        self.worldbank_client = WorldBankAPIClient()
        self.ocm_client = OpenChargeMapClient()
        self.llm_client = GroqAPIClient()
    
    # =========================================================================
    # MAIN ANALYSIS METHOD
    # =========================================================================
    
    def analyze_equity(
        self,
        latitude: float,
        longitude: float,
        country_code: str,
        radius_km: float = 10,
        location_name: str = "Unknown",
        # US-specific parameters
        state_fips: str = None,
        county_fips: str = None
    ) -> Dict[str, Any]:
        """
        Analyze equity for any location worldwide.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            country_code: ISO country code (e.g., "USA", "THA", "GBR")
            radius_km: Search radius for stations
            location_name: Human-readable location name
            state_fips: US state FIPS (only for USA)
            county_fips: US county FIPS (only for USA)
            
        Returns:
            Equity analysis dictionary
        """
        country_code = country_code.upper()
        
        print(f"🌍 Analyzing equity for {location_name} ({country_code})...")
        
        # Get charging stations (works globally!)
        print("   🔌 Fetching charging stations...")
        stations = self.ocm_client.get_parsed_stations(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            max_results=500
        )
        station_count = len(stations)
        
        # Get demographic data based on country
        if country_code == "USA" and state_fips and county_fips:
            print("   📊 Fetching US Census data...")
            demographics = self._get_us_demographics(state_fips, county_fips)
            data_source = "US Census Bureau"
        else:
            print(f"   📊 Fetching World Bank data for {country_code}...")
            demographics = self._get_global_demographics(country_code)
            data_source = "World Bank"
        
        if not demographics:
            return {
                "status": "partial",
                "message": "Demographics not available, showing infrastructure only",
                "location": location_name,
                "country_code": country_code,
                "infrastructure": {
                    "total_stations": station_count,
                    "search_radius_km": radius_km
                }
            }
        
        # Calculate equity metrics
        equity_score = self._calculate_global_equity_score(
            station_count=station_count,
            demographics=demographics,
            radius_km=radius_km,
            country_code=country_code
        )
        
        # Build result
        result = {
            "status": "success",
            "location": {
                "name": location_name,
                "country_code": country_code,
                "latitude": latitude,
                "longitude": longitude
            },
            "data_source": data_source,
            "demographics": demographics,
            "infrastructure": {
                "total_stations": station_count,
                "search_radius_km": radius_km,
                "stations_density": round(station_count / (3.14159 * radius_km ** 2), 2)
            },
            "equity_assessment": equity_score,
            "recommendations": self._generate_global_recommendations(
                country_code=country_code,
                equity_score=equity_score["score"],
                demographics=demographics,
                station_count=station_count
            )
        }
        
        return result
    
    # =========================================================================
    # DEMOGRAPHIC DATA METHODS
    # =========================================================================
    
    def _get_us_demographics(
        self,
        state_fips: str,
        county_fips: str
    ) -> Dict[str, Any]:
        """Get detailed US demographics from Census."""
        try:
            equity_data = self.census_client.get_equity_metrics(
                state_fips=state_fips,
                county_fips=county_fips
            )
            
            if not equity_data:
                return None
            
            return {
                "population": equity_data.get("population", 0),
                "income_per_capita": equity_data.get("median_income", 0),
                "income_level": self._get_us_income_level(equity_data.get("median_income", 0)),
                "poverty_rate": equity_data.get("poverty_rate", 0),
                "no_vehicle_rate": equity_data.get("no_vehicle_rate", 0),
                "data_level": "county",
                "region_name": equity_data.get("name", "Unknown")
            }
        except Exception as e:
            print(f"   ⚠️ Census error: {e}")
            return None
    
    def _get_global_demographics(self, country_code: str) -> Dict[str, Any]:
        """Get country-level demographics from World Bank."""
        try:
            profile = self.worldbank_client.get_country_profile(country_code)
            
            if profile.get("status") != "success":
                return None
            
            return {
                "population": profile["demographics"]["population"],
                "income_per_capita": profile["economics"]["gdp_per_capita"],
                "income_level": profile["economics"]["income_level"],
                "poverty_rate": profile["economics"]["poverty_rate"],
                "urban_percent": profile["demographics"]["urban_percent"],
                "electricity_access": profile["infrastructure"]["electricity_access"],
                "ev_readiness": profile["infrastructure"]["ev_readiness_score"],
                "vehicles_per_1000": profile["demographics"]["vehicles_per_1000"],
                "data_level": "country",
                "region_name": profile["country_name"]
            }
        except Exception as e:
            print(f"   ⚠️ World Bank error: {e}")
            return None
    
    def _get_us_income_level(self, median_income: float) -> str:
        """Categorize US income level."""
        if median_income >= 150000:
            return "Very High Income"
        elif median_income >= 100000:
            return "High Income"
        elif median_income >= 75000:
            return "Upper Middle Income"
        elif median_income >= 50000:
            return "Middle Income"
        elif median_income >= 35000:
            return "Lower Middle Income"
        else:
            return "Low Income"
    
    # =========================================================================
    # EQUITY SCORING
    # =========================================================================
    
    def _calculate_global_equity_score(
        self,
        station_count: int,
        demographics: Dict,
        radius_km: float,
        country_code: str
    ) -> Dict[str, Any]:
        """
        Calculate equity score that works globally.
        
        Adapts scoring based on country development level.
        """
        components = {}
        
        # 1. Infrastructure Access Score
        # Adjust benchmark based on country income level
        income_level = demographics.get("income_level", "Middle Income")
        
        if "High" in income_level:
            station_benchmark = 0.5  # High income: expect 0.5 stations per km²
        elif "Middle" in income_level:
            station_benchmark = 0.2  # Middle income: expect 0.2 stations per km²
        else:
            station_benchmark = 0.05  # Low income: expect 0.05 stations per km²
        
        area = 3.14159 * (radius_km ** 2)
        station_density = station_count / area
        access_ratio = min(station_density / station_benchmark, 2.0)  # Cap at 200%
        components["access"] = min(round(access_ratio * 50, 1), 100)
        
        # 2. Economic Readiness Score
        income = demographics.get("income_per_capita", 0)
        if income >= 50000:
            components["economic_readiness"] = 100
        elif income >= 30000:
            components["economic_readiness"] = 80
        elif income >= 15000:
            components["economic_readiness"] = 60
        elif income >= 5000:
            components["economic_readiness"] = 40
        else:
            components["economic_readiness"] = 20
        
        # 3. Poverty/Affordability Score
        poverty_rate = demographics.get("poverty_rate") or 0
        if poverty_rate <= 5:
            components["affordability"] = 100
        elif poverty_rate <= 10:
            components["affordability"] = 80
        elif poverty_rate <= 20:
            components["affordability"] = 60
        elif poverty_rate <= 30:
            components["affordability"] = 40
        else:
            components["affordability"] = 20
        
        # 4. Infrastructure Readiness (for non-US)
        if country_code != "USA":
            ev_readiness = demographics.get("ev_readiness", 50)
            electricity = demographics.get("electricity_access", 100)
            components["infrastructure_readiness"] = round((ev_readiness + electricity) / 2, 1)
        else:
            # US has good infrastructure
            components["infrastructure_readiness"] = 90
        
        # Calculate weighted score
        weights = {
            "access": 0.35,
            "economic_readiness": 0.25,
            "affordability": 0.20,
            "infrastructure_readiness": 0.20
        }
        
        total_score = sum(
            components[k] * weights[k] 
            for k in weights.keys()
        )
        
        # Determine grade
        if total_score >= 80:
            grade, rating = "A", "Excellent"
        elif total_score >= 65:
            grade, rating = "B", "Good"
        elif total_score >= 50:
            grade, rating = "C", "Fair"
        elif total_score >= 35:
            grade, rating = "D", "Poor"
        else:
            grade, rating = "F", "Critical"
        
        return {
            "score": round(total_score, 1),
            "grade": grade,
            "rating": rating,
            "components": components
        }
    
    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================
    
    def _generate_global_recommendations(
        self,
        country_code: str,
        equity_score: float,
        demographics: Dict,
        station_count: int
    ) -> List[Dict[str, str]]:
        """Generate recommendations based on global context."""
        recommendations = []
        
        income_level = demographics.get("income_level", "")
        poverty_rate = demographics.get("poverty_rate") or 0
        ev_readiness = demographics.get("ev_readiness", 100)
        
        # Low station count
        if station_count < 50:
            recommendations.append({
                "priority": "High",
                "category": "Infrastructure Expansion",
                "recommendation": "Significantly increase charging station deployment",
                "rationale": f"Only {station_count} stations found in search area"
            })
        
        # Developing country specific
        if "Low" in income_level:
            recommendations.append({
                "priority": "High",
                "category": "Affordability",
                "recommendation": "Implement subsidized public charging programs",
                "rationale": f"Lower income level requires affordability measures"
            })
            recommendations.append({
                "priority": "Medium",
                "category": "Infrastructure",
                "recommendation": "Focus on grid reliability before EV expansion",
                "rationale": "Stable electricity is prerequisite for EV adoption"
            })
        
        # High poverty
        if poverty_rate and poverty_rate > 15:
            recommendations.append({
                "priority": "High",
                "category": "Equity",
                "recommendation": "Target charging infrastructure in underserved areas",
                "rationale": f"Poverty rate of {poverty_rate}% indicates equity concerns"
            })
        
        # Low EV readiness
        if ev_readiness < 50:
            recommendations.append({
                "priority": "Medium",
                "category": "Policy",
                "recommendation": "Develop national EV adoption strategy",
                "rationale": f"EV readiness score of {ev_readiness} indicates need for policy support"
            })
        
        # General recommendations
        if len(recommendations) < 3:
            recommendations.append({
                "priority": "Standard",
                "category": "Community Engagement",
                "recommendation": "Conduct community needs assessment for charging locations",
                "rationale": "Ensure infrastructure meets local mobility patterns"
            })
        
        return recommendations
    
    # =========================================================================
    # AI INSIGHTS
    # =========================================================================
    
    def generate_ai_insights(self, analysis: Dict[str, Any]) -> str:
        """Generate AI-powered insights for global equity analysis."""
        if analysis.get("status") not in ["success", "partial"]:
            return "Unable to generate insights due to insufficient data."
        
        location = analysis.get("location", {})
        demographics = analysis.get("demographics", {})
        infra = analysis.get("infrastructure", {})
        equity = analysis.get("equity_assessment", {})
        
        prompt = f"""Analyze EV charging equity for this location:

LOCATION: {location.get('name', 'Unknown')} ({location.get('country_code', 'N/A')})

DEMOGRAPHICS:
- Population: {demographics.get('population', 'N/A'):,}
- Income Level: {demographics.get('income_level', 'N/A')}
- Income per Capita: ${demographics.get('income_per_capita', 0):,.0f}
- Poverty Rate: {demographics.get('poverty_rate', 'N/A')}%
- EV Readiness: {demographics.get('ev_readiness', 'N/A')}/100

INFRASTRUCTURE:
- Charging Stations: {infra.get('total_stations', 0)}
- Station Density: {infra.get('stations_density', 0)} per km²

EQUITY SCORE: {equity.get('score', 'N/A')}/100 (Grade: {equity.get('grade', 'N/A')})

Provide:
1. Key findings about EV charging equity
2. Comparison to global/regional standards
3. Top 3 actionable recommendations
4. Opportunities for improvement"""

        system_prompt = """You are a global EV infrastructure equity analyst.
Provide insights appropriate to the country's development level.
Be culturally aware and consider local context.
Focus on actionable, realistic recommendations."""

        return self.llm_client.generate(prompt, system_prompt, temperature=0.5)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🌍 Global Equity Analyzer")
    print("=" * 60)
    
    analyzer = GlobalEquityAnalyzer()
    print("✅ Analyzer initialized")
    
    # Test 1: USA (uses Census)
    print("\n" + "=" * 60)
    print("📍 Test 1: San Francisco, USA")
    usa_result = analyzer.analyze_equity(
        latitude=37.7749,
        longitude=-122.4194,
        country_code="USA",
        radius_km=10,
        location_name="San Francisco, CA",
        state_fips="06",
        county_fips="075"
    )
    
    if usa_result.get("status") == "success":
        print(f"✅ Analysis complete!")
        print(f"   Data Source: {usa_result['data_source']}")
        print(f"   Stations: {usa_result['infrastructure']['total_stations']}")
        print(f"   Equity Score: {usa_result['equity_assessment']['score']}/100")
        print(f"   Grade: {usa_result['equity_assessment']['grade']}")
    
    # Test 2: Thailand (uses World Bank)
    print("\n" + "=" * 60)
    print("📍 Test 2: Bangkok, Thailand")
    thailand_result = analyzer.analyze_equity(
        latitude=13.7563,
        longitude=100.5018,
        country_code="THA",
        radius_km=10,
        location_name="Bangkok, Thailand"
    )
    
    if thailand_result.get("status") == "success":
        print(f"✅ Analysis complete!")
        print(f"   Data Source: {thailand_result['data_source']}")
        print(f"   Stations: {thailand_result['infrastructure']['total_stations']}")
        print(f"   Equity Score: {thailand_result['equity_assessment']['score']}/100")
        print(f"   Grade: {thailand_result['equity_assessment']['grade']}")
    
    # Test 3: UK (uses World Bank)
    print("\n" + "=" * 60)
    print("📍 Test 3: London, UK")
    uk_result = analyzer.analyze_equity(
        latitude=51.5074,
        longitude=-0.1278,
        country_code="GBR",
        radius_km=10,
        location_name="London, UK"
    )
    
    if uk_result.get("status") == "success":
        print(f"✅ Analysis complete!")
        print(f"   Data Source: {uk_result['data_source']}")
        print(f"   Stations: {uk_result['infrastructure']['total_stations']}")
        print(f"   Equity Score: {uk_result['equity_assessment']['score']}/100")
        print(f"   Grade: {uk_result['equity_assessment']['grade']}")
    
    print("\n✅ Global Equity Analyzer working for multiple countries!")