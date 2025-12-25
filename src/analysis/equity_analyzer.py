"""
⚖️ Equity Analyzer
==================

Analyzes demographic equity in EV charging infrastructure access.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.census_client import CensusAPIClient
from src.data_access.openchargemap import OpenChargeMapClient
from src.data_access.groq_api import GroqAPIClient
from config.settings import EQUITY_WEIGHTS


class EquityAnalyzer:
    """
    Analyzes equity in EV charging infrastructure access.
    
    Examines:
    - Income-based disparities
    - Poverty rate correlations
    - Vehicle ownership patterns
    - Geographic equity
    - AI-powered recommendations
    """
    
    def __init__(self):
        """Initialize analyzer with API clients."""
        self.census_client = CensusAPIClient()
        self.ocm_client = OpenChargeMapClient()
        self.llm_client = GroqAPIClient()
        self.weights = EQUITY_WEIGHTS
    
    # =========================================================================
    # MAIN ANALYSIS METHODS
    # =========================================================================
    
    def analyze_county_equity(
        self,
        state_fips: str,
        county_fips: str,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        location_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive equity analysis for a county.
        
        Args:
            state_fips: State FIPS code
            county_fips: County FIPS code
            latitude: Center latitude for station search
            longitude: Center longitude for station search
            radius_km: Search radius for stations
            location_name: Human-readable location name
            
        Returns:
            Complete equity analysis dictionary
        """
        print(f"⚖️ Analyzing equity for {location_name}...")
        
        # Get demographic data
        print("   📊 Fetching demographic data...")
        demographics = self.census_client.get_equity_metrics(
            state_fips=state_fips,
            county_fips=county_fips
        )
        
        if not demographics:
            return {
                "status": "error",
                "message": "Failed to retrieve demographic data",
                "location": location_name
            }
        
        # Get charging stations
        print("   🔌 Fetching charging stations...")
        stations = self.ocm_client.get_parsed_stations(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            max_results=500
        )
        
        station_count = len(stations)
        
        # Calculate key metrics
        population = demographics.get("population", 0)
        median_income = demographics.get("median_income", 0)
        poverty_rate = demographics.get("poverty_rate", 0)
        no_vehicle_rate = demographics.get("no_vehicle_rate", 0)
        
        # Stations per capita
        stations_per_1000 = (station_count / population * 1000) if population > 0 else 0
        stations_per_10000 = stations_per_1000 * 10
        
        # Calculate equity score
        equity_score = self._calculate_equity_score(
            stations_per_1000=stations_per_1000,
            median_income=median_income,
            poverty_rate=poverty_rate,
            no_vehicle_rate=no_vehicle_rate
        )
        
        # Income bracket analysis
        income_analysis = self._analyze_income_level(median_income)
        
        # Access assessment
        access_assessment = self._assess_access_level(
            stations_per_1000=stations_per_1000,
            poverty_rate=poverty_rate
        )
        
        # Compile results
        analysis = {
            "status": "success",
            "location": {
                "name": location_name,
                "state_fips": state_fips,
                "county_fips": county_fips,
                "latitude": latitude,
                "longitude": longitude
            },
            "demographics": {
                "population": population,
                "median_income": median_income,
                "poverty_rate": poverty_rate,
                "no_vehicle_rate": no_vehicle_rate,
                "income_level": income_analysis["level"],
                "income_percentile": income_analysis["percentile"]
            },
            "infrastructure": {
                "total_stations": station_count,
                "stations_per_1000": round(stations_per_1000, 3),
                "stations_per_10000": round(stations_per_10000, 2),
                "search_radius_km": radius_km
            },
            "equity_assessment": {
                "score": equity_score["score"],
                "grade": equity_score["grade"],
                "rating": equity_score["rating"],
                "components": equity_score["components"]
            },
            "access_assessment": access_assessment,
            "recommendations": self._generate_recommendations(
                equity_score=equity_score["score"],
                poverty_rate=poverty_rate,
                stations_per_1000=stations_per_1000,
                income_level=income_analysis["level"]
            )
        }
        
        return analysis
    
    def generate_ai_insights(self, analysis: Dict[str, Any]) -> str:
        """
        Generate AI-powered equity insights.
        
        Args:
            analysis: Equity analysis results
            
        Returns:
            AI-generated insights text
        """
        if analysis.get("status") != "success":
            return "Unable to generate insights due to insufficient data."
        
        data = {
            "population": analysis["demographics"]["population"],
            "median_income": analysis["demographics"]["median_income"],
            "poverty_rate": analysis["demographics"]["poverty_rate"],
            "no_vehicle_rate": analysis["demographics"]["no_vehicle_rate"],
            "stations": analysis["infrastructure"]["total_stations"],
            "stations_per_1000": analysis["infrastructure"]["stations_per_1000"],
            "location": analysis["location"]["name"]
        }
        
        return self.llm_client.analyze_equity(data)
    
    # =========================================================================
    # EQUITY SCORING
    # =========================================================================
    
    def _calculate_equity_score(
        self,
        stations_per_1000: float,
        median_income: float,
        poverty_rate: float,
        no_vehicle_rate: float
    ) -> Dict[str, Any]:
        """
        Calculate composite equity score (0-100).
        
        Higher score = better equity situation
        """
        components = {}
        
        # 1. Access Score (based on stations per capita)
        # Benchmark: 0.5 stations per 1000 people is considered adequate
        if stations_per_1000 >= 1.0:
            access_score = 100
        elif stations_per_1000 >= 0.5:
            access_score = 70 + (stations_per_1000 - 0.5) * 60
        elif stations_per_1000 >= 0.1:
            access_score = 30 + (stations_per_1000 - 0.1) * 100
        else:
            access_score = stations_per_1000 * 300
        
        components["access"] = min(round(access_score, 1), 100)
        
        # 2. Affordability Score (inverse of poverty rate)
        # Lower poverty = higher score
        if poverty_rate <= 5:
            affordability_score = 100
        elif poverty_rate <= 10:
            affordability_score = 80 - (poverty_rate - 5) * 4
        elif poverty_rate <= 20:
            affordability_score = 60 - (poverty_rate - 10) * 3
        else:
            affordability_score = max(30 - (poverty_rate - 20) * 1.5, 0)
        
        components["affordability"] = round(affordability_score, 1)
        
        # 3. Mobility Score (inverse of no-vehicle rate)
        # Higher vehicle ownership = more likely to benefit from EV infrastructure
        # But also consider that low vehicle areas need transit-accessible charging
        if no_vehicle_rate <= 5:
            mobility_score = 90
        elif no_vehicle_rate <= 10:
            mobility_score = 70 + (10 - no_vehicle_rate) * 4
        elif no_vehicle_rate <= 20:
            mobility_score = 50 + (20 - no_vehicle_rate) * 2
        else:
            mobility_score = max(50 - (no_vehicle_rate - 20), 20)
        
        components["mobility"] = round(mobility_score, 1)
        
        # 4. Income Alignment Score
        # Check if infrastructure matches income level
        # High income should have high access, low income needs subsidized access
        national_median = 75000  # Approximate US median
        income_ratio = median_income / national_median
        
        if income_ratio >= 1.5:  # High income area
            # Should have good access
            income_score = min(access_score * 1.1, 100)
        elif income_ratio >= 0.8:  # Middle income
            income_score = 70 + (income_ratio - 0.8) * 43
        else:  # Low income - needs extra support
            # Penalize if low income AND low access
            if stations_per_1000 < 0.3:
                income_score = 40
            else:
                income_score = 60
        
        components["income_alignment"] = round(income_score, 1)
        
        # Weighted composite score
        weights = self.weights
        composite = (
            components["access"] * weights.get("income", 0.35) +
            components["affordability"] * weights.get("poverty", 0.25) +
            components["mobility"] * weights.get("vehicle_access", 0.20) +
            components["income_alignment"] * weights.get("population_density", 0.20)
        )
        
        # Determine grade
        if composite >= 85:
            grade, rating = "A", "Excellent"
        elif composite >= 70:
            grade, rating = "B", "Good"
        elif composite >= 55:
            grade, rating = "C", "Fair"
        elif composite >= 40:
            grade, rating = "D", "Poor"
        else:
            grade, rating = "F", "Critical"
        
        return {
            "score": round(composite, 1),
            "grade": grade,
            "rating": rating,
            "components": components
        }
    
    # =========================================================================
    # HELPER ANALYSIS METHODS
    # =========================================================================
    
    def _analyze_income_level(self, median_income: float) -> Dict[str, Any]:
        """Categorize income level relative to national benchmarks."""
        # US income percentile approximations
        if median_income >= 150000:
            return {"level": "Very High", "percentile": 95}
        elif median_income >= 100000:
            return {"level": "High", "percentile": 80}
        elif median_income >= 75000:
            return {"level": "Upper Middle", "percentile": 60}
        elif median_income >= 50000:
            return {"level": "Middle", "percentile": 40}
        elif median_income >= 35000:
            return {"level": "Lower Middle", "percentile": 25}
        else:
            return {"level": "Low", "percentile": 10}
    
    def _assess_access_level(
        self,
        stations_per_1000: float,
        poverty_rate: float
    ) -> Dict[str, Any]:
        """Assess charging access level considering socioeconomic factors."""
        # Determine access adequacy
        if stations_per_1000 >= 0.8:
            access_level = "High"
            access_adequate = True
        elif stations_per_1000 >= 0.4:
            access_level = "Moderate"
            access_adequate = True
        elif stations_per_1000 >= 0.1:
            access_level = "Limited"
            access_adequate = False
        else:
            access_level = "Very Limited"
            access_adequate = False
        
        # Determine need level (higher poverty = higher need for accessible charging)
        if poverty_rate >= 20:
            need_level = "Critical"
        elif poverty_rate >= 15:
            need_level = "High"
        elif poverty_rate >= 10:
            need_level = "Moderate"
        else:
            need_level = "Standard"
        
        # Determine priority
        if not access_adequate and need_level in ["Critical", "High"]:
            priority = "Urgent"
            priority_score = 5
        elif not access_adequate:
            priority = "High"
            priority_score = 4
        elif need_level in ["Critical", "High"]:
            priority = "Moderate"
            priority_score = 3
        else:
            priority = "Standard"
            priority_score = 2
        
        return {
            "access_level": access_level,
            "access_adequate": access_adequate,
            "need_level": need_level,
            "priority": priority,
            "priority_score": priority_score,
            "description": f"{access_level} access with {need_level.lower()} community need"
        }
    
    def _generate_recommendations(
        self,
        equity_score: float,
        poverty_rate: float,
        stations_per_1000: float,
        income_level: str
    ) -> List[Dict[str, str]]:
        """Generate targeted recommendations based on analysis."""
        recommendations = []
        
        # Low access recommendations
        if stations_per_1000 < 0.3:
            recommendations.append({
                "priority": "High",
                "category": "Infrastructure Expansion",
                "recommendation": "Significantly increase charging station deployment",
                "rationale": f"Current density ({stations_per_1000:.2f}/1000) is below minimum threshold"
            })
        
        # High poverty recommendations
        if poverty_rate > 15:
            recommendations.append({
                "priority": "High",
                "category": "Affordability",
                "recommendation": "Implement subsidized charging programs",
                "rationale": f"High poverty rate ({poverty_rate}%) requires affordability measures"
            })
            recommendations.append({
                "priority": "Medium",
                "category": "Location Strategy",
                "recommendation": "Prioritize charging at affordable housing and public facilities",
                "rationale": "Increase access for low-income residents"
            })
        
        # Income-specific recommendations
        if income_level in ["Low", "Lower Middle"]:
            recommendations.append({
                "priority": "Medium",
                "category": "Financial Support",
                "recommendation": "Partner with utilities for reduced-rate charging",
                "rationale": "Make EV ownership more accessible for lower-income households"
            })
        
        # Low equity score recommendations
        if equity_score < 50:
            recommendations.append({
                "priority": "High",
                "category": "Equity Focus",
                "recommendation": "Conduct detailed equity mapping study",
                "rationale": f"Low equity score ({equity_score}) indicates significant disparities"
            })
        
        # General best practices
        if len(recommendations) < 3:
            recommendations.append({
                "priority": "Standard",
                "category": "Community Engagement",
                "recommendation": "Engage community in charging location planning",
                "rationale": "Ensure infrastructure meets local needs"
            })
        
        return recommendations
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate text report from equity analysis."""
        if analysis.get("status") != "success":
            return f"Analysis failed: {analysis.get('message', 'Unknown error')}"
        
        location = analysis["location"]
        demo = analysis["demographics"]
        infra = analysis["infrastructure"]
        equity = analysis["equity_assessment"]
        access = analysis["access_assessment"]
        
        report = f"""
================================================================================
EV CHARGING EQUITY ANALYSIS REPORT
================================================================================

LOCATION: {location['name']}
State FIPS: {location['state_fips']} | County FIPS: {location['county_fips']}

--------------------------------------------------------------------------------
DEMOGRAPHIC PROFILE
--------------------------------------------------------------------------------
Population: {demo['population']:,}
Median Household Income: ${demo['median_income']:,}
Income Level: {demo['income_level']} (Est. {demo['income_percentile']}th percentile)
Poverty Rate: {demo['poverty_rate']}%
Households Without Vehicle: {demo['no_vehicle_rate']}%

--------------------------------------------------------------------------------
INFRASTRUCTURE METRICS
--------------------------------------------------------------------------------
Total Charging Stations: {infra['total_stations']}
Stations per 1,000 People: {infra['stations_per_1000']:.3f}
Stations per 10,000 People: {infra['stations_per_10000']:.2f}
Search Radius: {infra['search_radius_km']} km

--------------------------------------------------------------------------------
EQUITY ASSESSMENT
--------------------------------------------------------------------------------
Overall Equity Score: {equity['score']}/100
Grade: {equity['grade']} ({equity['rating']})

Component Scores:
  - Access: {equity['components']['access']}/100
  - Affordability: {equity['components']['affordability']}/100
  - Mobility: {equity['components']['mobility']}/100
  - Income Alignment: {equity['components']['income_alignment']}/100

--------------------------------------------------------------------------------
ACCESS ASSESSMENT
--------------------------------------------------------------------------------
Access Level: {access['access_level']}
Access Adequate: {'Yes' if access['access_adequate'] else 'No'}
Community Need Level: {access['need_level']}
Priority for Improvement: {access['priority']}

--------------------------------------------------------------------------------
RECOMMENDATIONS
--------------------------------------------------------------------------------
"""
        
        for i, rec in enumerate(analysis["recommendations"], 1):
            report += f"""
{i}. [{rec['priority']}] {rec['category']}
   Recommendation: {rec['recommendation']}
   Rationale: {rec['rationale']}
"""
        
        report += "\n" + "=" * 80
        return report


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("⚖️ Equity Analyzer")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = EquityAnalyzer()
    print("✅ Analyzer initialized")
    
    # Analyze San Francisco County
    print("\n📍 Analyzing equity for San Francisco County...")
    analysis = analyzer.analyze_county_equity(
        state_fips="06",
        county_fips="075",
        latitude=37.7749,
        longitude=-122.4194,
        radius_km=10,
        location_name="San Francisco County, CA"
    )
    
    if analysis["status"] == "success":
        print(f"\n✅ Analysis Complete!")
        print(f"   Population: {analysis['demographics']['population']:,}")
        print(f"   Median Income: ${analysis['demographics']['median_income']:,}")
        print(f"   Poverty Rate: {analysis['demographics']['poverty_rate']}%")
        print(f"   Stations: {analysis['infrastructure']['total_stations']}")
        print(f"   Stations per 1000: {analysis['infrastructure']['stations_per_1000']:.3f}")
        print(f"   Equity Score: {analysis['equity_assessment']['score']}/100 ({analysis['equity_assessment']['grade']})")
        
        # Generate AI insights
        print("\n🤖 Generating AI equity insights...")
        insights = analyzer.generate_ai_insights(analysis)
        print(f"\n{insights[:500]}...")
        
        # Print report
        print("\n" + "=" * 60)
        print("FULL REPORT:")
        print(analyzer.generate_report(analysis))
    else:
        print(f"❌ Analysis failed: {analysis.get('message')}")