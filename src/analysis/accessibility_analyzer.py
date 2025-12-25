"""
🏪 Accessibility Analyzer
=========================

Analyzes accessibility and convenience of charging stations.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.openchargemap import OpenChargeMapClient
from src.data_access.overpass_api import OverpassAPIClient
from src.data_access.weather_api import WeatherAPIClient
from src.data_access.groq_api import GroqAPIClient
from config.settings import CONVENIENCE_WEIGHTS


class AccessibilityAnalyzer:
    """
    Analyzes accessibility and convenience of EV charging stations.
    
    Examines:
    - Nearby amenities (dining, shopping, services)
    - Public transit access
    - Weather/climate impact
    - Overall convenience scoring
    """
    
    def __init__(self):
        """Initialize analyzer with API clients."""
        self.ocm_client = OpenChargeMapClient()
        self.overpass_client = OverpassAPIClient()
        self.weather_client = WeatherAPIClient()
        self.llm_client = GroqAPIClient()
        self.weights = CONVENIENCE_WEIGHTS
    
    # =========================================================================
    # MAIN ANALYSIS METHODS
    # =========================================================================
    
    def analyze_station_accessibility(
        self,
        station: Dict[str, Any],
        amenity_radius_m: int = 500
    ) -> Dict[str, Any]:
        """
        Analyze accessibility for a single charging station.
        
        Args:
            station: Parsed station dictionary
            amenity_radius_m: Radius to search for amenities
            
        Returns:
            Accessibility analysis for the station
        """
        lat = station.get("location", {}).get("latitude")
        lon = station.get("location", {}).get("longitude")
        
        if not lat or not lon:
            return {"status": "error", "message": "No location data"}
        
        # Get nearby POIs
        pois = self.overpass_client.get_all_pois(lat, lon, amenity_radius_m)
        
        # Get convenience score
        convenience = self.overpass_client.calculate_convenience_score(
            lat, lon, amenity_radius_m
        )
        
        # Get transit stops
        transit = self.overpass_client.get_transit_stops(lat, lon, amenity_radius_m)
        
        return {
            "station_id": station.get("id"),
            "station_name": station.get("name"),
            "location": {"latitude": lat, "longitude": lon},
            "convenience_score": convenience["total_score"],
            "convenience_grade": convenience["grade"],
            "category_scores": convenience["category_scores"],
            "poi_counts": convenience["category_counts"],
            "transit_stops": len(transit),
            "transit_types": self._count_transit_types(transit),
            "amenity_radius_m": amenity_radius_m
        }
    
    def analyze_location_accessibility(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        location_name: str = "Unknown",
        sample_size: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze accessibility for all stations in an area.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius for stations
            location_name: Human-readable location name
            sample_size: Number of stations to analyze in detail
            
        Returns:
            Complete accessibility analysis
        """
        print(f"🏪 Analyzing accessibility for {location_name}...")
        
        # Get charging stations
        print("   🔌 Fetching charging stations...")
        stations = self.ocm_client.get_parsed_stations(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            max_results=200
        )
        
        if not stations:
            return {
                "status": "error",
                "message": "No charging stations found",
                "location": location_name
            }
        
        # Analyze sample of stations for detailed accessibility
        print(f"   📊 Analyzing {min(sample_size, len(stations))} stations in detail...")
        sample_stations = stations[:sample_size]
        detailed_analyses = []
        
        for i, station in enumerate(sample_stations):
            analysis = self.analyze_station_accessibility(station)
            detailed_analyses.append(analysis)
            print(f"      Station {i+1}/{len(sample_stations)}: {analysis.get('convenience_grade', 'N/A')}")
        
        # Calculate aggregate statistics
        scores = [a["convenience_score"] for a in detailed_analyses if "convenience_score" in a]
        
        avg_score = sum(scores) / len(scores) if scores else 0
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        # Grade distribution
        grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for a in detailed_analyses:
            grade = a.get("convenience_grade", "F")
            grade_dist[grade] = grade_dist.get(grade, 0) + 1
        
        # Get weather/climate data
        print("   🌤️ Fetching climate data...")
        climate = self.weather_client.analyze_ev_range_impact(latitude, longitude)
        
        # Compile results
        analysis = {
            "status": "success",
            "location": {
                "name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km
            },
            "summary": {
                "total_stations": len(stations),
                "stations_analyzed": len(detailed_analyses),
                "avg_convenience_score": round(avg_score, 1),
                "min_convenience_score": round(min_score, 1),
                "max_convenience_score": round(max_score, 1),
                "overall_grade": self._calculate_overall_grade(avg_score)
            },
            "grade_distribution": grade_dist,
            "climate_impact": climate,
            "detailed_analyses": detailed_analyses,
            "top_stations": self._get_top_stations(detailed_analyses, 5),
            "bottom_stations": self._get_bottom_stations(detailed_analyses, 5)
        }
        
        return analysis
    
    def generate_ai_insights(self, analysis: Dict[str, Any]) -> str:
        """
        Generate AI-powered accessibility insights.
        
        Args:
            analysis: Accessibility analysis results
            
        Returns:
            AI-generated insights text
        """
        if analysis.get("status") != "success":
            return "Unable to generate insights due to insufficient data."
        
        summary = analysis["summary"]
        climate = analysis.get("climate_impact", {})
        
        prompt = f"""Analyze EV charging station accessibility for {analysis['location']['name']}:

CONVENIENCE METRICS:
- Total Stations: {summary['total_stations']}
- Average Convenience Score: {summary['avg_convenience_score']}/10
- Score Range: {summary['min_convenience_score']} - {summary['max_convenience_score']}
- Overall Grade: {summary['overall_grade']}

GRADE DISTRIBUTION:
{analysis['grade_distribution']}

CLIMATE IMPACT:
- Current EV Range Factor: {climate.get('current', {}).get('range_percentage', 'N/A')}
- Impact Level: {climate.get('impact', {}).get('level', 'N/A')}

Provide insights on:
1. Overall accessibility quality
2. Key strengths and weaknesses
3. Recommendations for improvement"""

        system_prompt = """You are an EV charging infrastructure analyst focusing on accessibility.
Provide concise, actionable insights about charging station convenience and accessibility.
Consider amenities, transit access, and climate factors."""

        return self.llm_client.generate(prompt, system_prompt, temperature=0.5)
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _count_transit_types(self, transit_stops: List[Dict]) -> Dict[str, int]:
        """Count transit stops by type."""
        counts = {}
        for stop in transit_stops:
            transit_type = stop.get("transit_type", "unknown")
            counts[transit_type] = counts.get(transit_type, 0) + 1
        return counts
    
    def _calculate_overall_grade(self, avg_score: float) -> str:
        """Calculate overall grade from average score."""
        if avg_score >= 8.5:
            return "A"
        elif avg_score >= 7.0:
            return "B"
        elif avg_score >= 5.0:
            return "C"
        elif avg_score >= 3.0:
            return "D"
        else:
            return "F"
    
    def _get_top_stations(
        self,
        analyses: List[Dict],
        n: int = 5
    ) -> List[Dict]:
        """Get top N stations by convenience score."""
        sorted_analyses = sorted(
            analyses,
            key=lambda x: x.get("convenience_score", 0),
            reverse=True
        )
        return [
            {
                "name": a.get("station_name"),
                "score": a.get("convenience_score"),
                "grade": a.get("convenience_grade"),
                "transit_stops": a.get("transit_stops", 0)
            }
            for a in sorted_analyses[:n]
        ]
    
    def _get_bottom_stations(
        self,
        analyses: List[Dict],
        n: int = 5
    ) -> List[Dict]:
        """Get bottom N stations by convenience score."""
        sorted_analyses = sorted(
            analyses,
            key=lambda x: x.get("convenience_score", 0)
        )
        return [
            {
                "name": a.get("station_name"),
                "score": a.get("convenience_score"),
                "grade": a.get("convenience_grade"),
                "transit_stops": a.get("transit_stops", 0)
            }
            for a in sorted_analyses[:n]
        ]
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate text report from accessibility analysis."""
        if analysis.get("status") != "success":
            return f"Analysis failed: {analysis.get('message', 'Unknown error')}"
        
        location = analysis["location"]
        summary = analysis["summary"]
        climate = analysis.get("climate_impact", {})
        
        report = f"""
================================================================================
EV CHARGING ACCESSIBILITY ANALYSIS REPORT
================================================================================

LOCATION: {location['name']}
Coordinates: ({location['latitude']}, {location['longitude']})
Search Radius: {location['radius_km']} km

--------------------------------------------------------------------------------
SUMMARY
--------------------------------------------------------------------------------
Total Stations: {summary['total_stations']}
Stations Analyzed: {summary['stations_analyzed']}
Average Convenience Score: {summary['avg_convenience_score']}/10
Score Range: {summary['min_convenience_score']} - {summary['max_convenience_score']}
Overall Grade: {summary['overall_grade']}

--------------------------------------------------------------------------------
GRADE DISTRIBUTION
--------------------------------------------------------------------------------
"""
        for grade, count in sorted(analysis["grade_distribution"].items()):
            bar = "█" * count
            report += f"  Grade {grade}: {count} stations {bar}\n"
        
        report += f"""
--------------------------------------------------------------------------------
CLIMATE IMPACT ON EV CHARGING
--------------------------------------------------------------------------------
Current Temperature: {climate.get('current', {}).get('temperature', 'N/A')}°C
EV Range Factor: {climate.get('current', {}).get('range_percentage', 'N/A')}
Impact Level: {climate.get('impact', {}).get('level', 'N/A')}
Recommendation: {climate.get('impact', {}).get('recommendation', 'N/A')}

--------------------------------------------------------------------------------
TOP 5 MOST ACCESSIBLE STATIONS
--------------------------------------------------------------------------------
"""
        for i, station in enumerate(analysis["top_stations"], 1):
            report += f"  {i}. {station['name']}\n"
            report += f"     Score: {station['score']}/10 ({station['grade']}) | Transit: {station['transit_stops']} stops\n"
        
        report += """
--------------------------------------------------------------------------------
BOTTOM 5 LEAST ACCESSIBLE STATIONS
--------------------------------------------------------------------------------
"""
        for i, station in enumerate(analysis["bottom_stations"], 1):
            report += f"  {i}. {station['name']}\n"
            report += f"     Score: {station['score']}/10 ({station['grade']}) | Transit: {station['transit_stops']} stops\n"
        
        report += "\n" + "=" * 80
        return report


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🏪 Accessibility Analyzer")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = AccessibilityAnalyzer()
    print("✅ Analyzer initialized")
    
    # Analyze San Francisco
    print("\n📍 Analyzing accessibility for San Francisco...")
    analysis = analyzer.analyze_location_accessibility(
        latitude=37.7749,
        longitude=-122.4194,
        radius_km=5,
        location_name="San Francisco, CA",
        sample_size=5  # Analyze 5 stations to keep test quick
    )
    
    if analysis["status"] == "success":
        print(f"\n✅ Analysis Complete!")
        print(f"   Total Stations: {analysis['summary']['total_stations']}")
        print(f"   Avg Convenience Score: {analysis['summary']['avg_convenience_score']}/10")
        print(f"   Overall Grade: {analysis['summary']['overall_grade']}")
        
        # Climate impact
        climate = analysis.get("climate_impact", {})
        print(f"\n🌤️ Climate Impact:")
        print(f"   EV Range: {climate.get('current', {}).get('range_percentage', 'N/A')}")
        print(f"   Impact: {climate.get('impact', {}).get('level', 'N/A')}")
        
        # Generate AI insights
        print("\n🤖 Generating AI insights...")
        insights = analyzer.generate_ai_insights(analysis)
        print(f"\n{insights[:500]}...")
        
        # Print report
        print("\n" + "=" * 60)
        print("FULL REPORT:")
        print(analyzer.generate_report(analysis))
    else:
        print(f"❌ Analysis failed: {analysis.get('message')}")