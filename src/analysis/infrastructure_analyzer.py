"""
🔌 Infrastructure Analyzer
==========================

Analyzes EV charging infrastructure coverage, gaps, and capacity.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.openchargemap import OpenChargeMapClient
from src.data_access.groq_api import GroqAPIClient


class InfrastructureAnalyzer:
    """
    Analyzes EV charging infrastructure.
    
    Provides:
    - Coverage analysis
    - Gap identification
    - Capacity assessment
    - Operator distribution
    - AI-powered insights
    """
    
    def __init__(self):
        """Initialize analyzer with API clients."""
        self.ocm_client = OpenChargeMapClient()
        self.llm_client = GroqAPIClient()
    
    # =========================================================================
    # MAIN ANALYSIS METHODS
    # =========================================================================
    
    def analyze_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        location_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive infrastructure analysis for a location.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in km
            location_name: Human-readable location name
            
        Returns:
            Complete analysis dictionary
        """
        print(f"📍 Analyzing infrastructure for {location_name}...")
        
        # Fetch stations
        stations = self.ocm_client.get_parsed_stations(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            max_results=500
        )
        
        if not stations:
            return {
                "status": "error",
                "message": "No charging stations found",
                "location": location_name
            }
        
        # Calculate statistics
        stats = self.ocm_client.get_station_statistics(stations)
        
        # Analyze coverage
        coverage = self._analyze_coverage(stations, radius_km)
        
        # Analyze operators
        operators = self._analyze_operators(stations)
        
        # Analyze charging levels
        levels = self._analyze_charging_levels(stations)
        
        # Identify gaps
        gaps = self._identify_gaps(stations, latitude, longitude, radius_km)
        
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
                "total_stations": stats["total_stations"],
                "total_connectors": stats["total_connectors"],
                "fast_chargers": stats["fast_chargers"],
                "fast_charger_ratio": round(stats["fast_chargers"] / max(stats["total_connectors"], 1) * 100, 1),
                "unique_operators": len(stats["operators"]),
                "operational_stations": stats["operational"],
                "public_access": stats["public_access"]
            },
            "coverage": coverage,
            "operators": operators,
            "charging_levels": levels,
            "power_statistics": stats["power_stats"],
            "gaps": gaps,
            "stations": stations  # Raw station data for visualization
        }
        
        return analysis
    
    def generate_ai_insights(self, analysis: Dict[str, Any]) -> str:
        """
        Generate AI-powered insights for the analysis.
        
        Args:
            analysis: Analysis results dictionary
            
        Returns:
            AI-generated insights text
        """
        if analysis.get("status") != "success":
            return "Unable to generate insights due to insufficient data."
        
        # Prepare data for LLM
        data = {
            "total_stations": analysis["summary"]["total_stations"],
            "total_connectors": analysis["summary"]["total_connectors"],
            "fast_chargers": analysis["summary"]["fast_chargers"],
            "operators": analysis["operators"]["distribution"],
            "power_stats": analysis["power_statistics"],
            "location": analysis["location"]["name"],
            "radius_km": analysis["location"]["radius_km"],
            "gaps": analysis["gaps"]["summary"]
        }
        
        return self.llm_client.analyze_infrastructure(data)
    
    # =========================================================================
    # COVERAGE ANALYSIS
    # =========================================================================
    
    def _analyze_coverage(
        self,
        stations: List[Dict],
        radius_km: float
    ) -> Dict[str, Any]:
        """Analyze coverage density and distribution."""
        if not stations:
            return {"density": 0, "distribution": "none"}
        
        # Calculate area
        area_sq_km = math.pi * (radius_km ** 2)
        
        # Station density
        density = len(stations) / area_sq_km
        
        # Connector density
        total_connectors = sum(s.get("num_points", 1) for s in stations)
        connector_density = total_connectors / area_sq_km
        
        # Distribution analysis (quadrant-based)
        distribution = self._calculate_distribution(stations)
        
        # Coverage rating
        if density >= 5:
            rating = "Excellent"
            score = 5
        elif density >= 3:
            rating = "Good"
            score = 4
        elif density >= 1:
            rating = "Moderate"
            score = 3
        elif density >= 0.5:
            rating = "Limited"
            score = 2
        else:
            rating = "Poor"
            score = 1
        
        return {
            "area_sq_km": round(area_sq_km, 2),
            "station_density": round(density, 2),
            "connector_density": round(connector_density, 2),
            "stations_per_sq_km": round(density, 2),
            "connectors_per_sq_km": round(connector_density, 2),
            "distribution_score": distribution["score"],
            "distribution_rating": distribution["rating"],
            "coverage_rating": rating,
            "coverage_score": score
        }
    
    def _calculate_distribution(self, stations: List[Dict]) -> Dict[str, Any]:
        """Calculate how evenly distributed stations are."""
        if len(stations) < 4:
            return {"score": 0.5, "rating": "Insufficient data"}
        
        # Get center point
        lats = [s["location"]["latitude"] for s in stations if s.get("location")]
        lons = [s["location"]["longitude"] for s in stations if s.get("location")]
        
        if not lats or not lons:
            return {"score": 0.5, "rating": "No location data"}
        
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        # Count stations in each quadrant
        quadrants = {"NE": 0, "NW": 0, "SE": 0, "SW": 0}
        
        for s in stations:
            loc = s.get("location", {})
            lat, lon = loc.get("latitude"), loc.get("longitude")
            if lat and lon:
                if lat >= center_lat:
                    quadrants["NE" if lon >= center_lon else "NW"] += 1
                else:
                    quadrants["SE" if lon >= center_lon else "SW"] += 1
        
        # Calculate evenness (0-1, where 1 is perfectly even)
        total = sum(quadrants.values())
        expected = total / 4
        variance = sum((v - expected) ** 2 for v in quadrants.values()) / 4
        max_variance = (total - expected) ** 2  # Worst case: all in one quadrant
        
        if max_variance == 0:
            score = 1.0
        else:
            score = 1 - (variance / max_variance)
        
        # Rating
        if score >= 0.8:
            rating = "Even"
        elif score >= 0.6:
            rating = "Moderate"
        elif score >= 0.4:
            rating = "Uneven"
        else:
            rating = "Clustered"
        
        return {
            "score": round(score, 2),
            "rating": rating,
            "quadrants": quadrants
        }
    
    # =========================================================================
    # OPERATOR ANALYSIS
    # =========================================================================
    
    def _analyze_operators(self, stations: List[Dict]) -> Dict[str, Any]:
        """Analyze operator distribution and market share."""
        operators = defaultdict(lambda: {"count": 0, "connectors": 0})
        
        for station in stations:
            op_name = station.get("operator", {}).get("name", "Unknown")
            operators[op_name]["count"] += 1
            operators[op_name]["connectors"] += station.get("num_points", 1)
        
        # Sort by station count
        sorted_ops = sorted(
            operators.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        total_stations = len(stations)
        total_connectors = sum(s.get("num_points", 1) for s in stations)
        
        # Calculate market share
        distribution = {}
        for name, data in sorted_ops[:10]:  # Top 10
            distribution[name] = {
                "stations": data["count"],
                "connectors": data["connectors"],
                "market_share": round(data["count"] / total_stations * 100, 1)
            }
        
        # Concentration analysis (HHI - Herfindahl-Hirschman Index)
        hhi = sum((d["market_share"] / 100) ** 2 for d in distribution.values()) * 10000
        
        if hhi < 1500:
            concentration = "Competitive"
        elif hhi < 2500:
            concentration = "Moderate"
        else:
            concentration = "Concentrated"
        
        return {
            "total_operators": len(operators),
            "distribution": distribution,
            "top_operator": sorted_ops[0][0] if sorted_ops else "N/A",
            "hhi_index": round(hhi, 0),
            "market_concentration": concentration
        }
    
    # =========================================================================
    # CHARGING LEVEL ANALYSIS
    # =========================================================================
    
    def _analyze_charging_levels(self, stations: List[Dict]) -> Dict[str, Any]:
        """Analyze charging speed/level distribution."""
        levels = {
            "Level 1 (Slow)": {"count": 0, "power_range": "< 5 kW"},
            "Level 2 (Medium)": {"count": 0, "power_range": "5-22 kW"},
            "Level 3 (Fast)": {"count": 0, "power_range": "22-50 kW"},
            "DC Fast (Ultra)": {"count": 0, "power_range": "> 50 kW"}
        }
        
        for station in stations:
            for conn in station.get("connections", []):
                power = conn.get("power_kw", 0) or 0
                qty = conn.get("quantity", 1)
                
                if power < 5:
                    levels["Level 1 (Slow)"]["count"] += qty
                elif power < 22:
                    levels["Level 2 (Medium)"]["count"] += qty
                elif power <= 50:
                    levels["Level 3 (Fast)"]["count"] += qty
                else:
                    levels["DC Fast (Ultra)"]["count"] += qty
        
        total = sum(l["count"] for l in levels.values())
        
        # Add percentages
        for level_data in levels.values():
            level_data["percentage"] = round(
                level_data["count"] / max(total, 1) * 100, 1
            )
        
        return {
            "distribution": levels,
            "total_connectors": total,
            "fast_charging_available": levels["Level 3 (Fast)"]["count"] + levels["DC Fast (Ultra)"]["count"] > 0
        }
    
    # =========================================================================
    # GAP IDENTIFICATION
    # =========================================================================
    
    def _identify_gaps(
        self,
        stations: List[Dict],
        center_lat: float,
        center_lon: float,
        radius_km: float
    ) -> Dict[str, Any]:
        """Identify infrastructure gaps."""
        gaps = []
        
        # Check for fast charging gap
        fast_chargers = sum(
            1 for s in stations
            for c in s.get("connections", [])
            if (c.get("power_kw") or 0) > 50
        )
        
        if fast_chargers < len(stations) * 0.1:
            gaps.append({
                "type": "fast_charging",
                "severity": "high",
                "description": f"Only {fast_chargers} DC fast chargers available"
            })
        
        # Check for operator diversity
        operators = set(s.get("operator", {}).get("name") for s in stations)
        if len(operators) < 3:
            gaps.append({
                "type": "operator_diversity",
                "severity": "medium",
                "description": f"Limited operator diversity ({len(operators)} operators)"
            })
        
        # Check coverage density
        area = math.pi * (radius_km ** 2)
        density = len(stations) / area
        
        if density < 1:
            gaps.append({
                "type": "coverage_density",
                "severity": "high",
                "description": f"Low station density ({density:.2f}/sq km)"
            })
        
        # Check 24/7 availability (if data available)
        # This would require additional data not always in OCM
        
        return {
            "gaps_identified": len(gaps),
            "gaps": gaps,
            "summary": "; ".join(g["description"] for g in gaps) if gaps else "No significant gaps identified"
        }
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate text report from analysis."""
        if analysis.get("status") != "success":
            return f"Analysis failed: {analysis.get('message', 'Unknown error')}"
        
        location = analysis["location"]
        summary = analysis["summary"]
        coverage = analysis["coverage"]
        operators = analysis["operators"]
        
        report = f"""
================================================================================
EV CHARGING INFRASTRUCTURE ANALYSIS REPORT
================================================================================

LOCATION: {location['name']}
Coordinates: ({location['latitude']}, {location['longitude']})
Search Radius: {location['radius_km']} km

--------------------------------------------------------------------------------
SUMMARY
--------------------------------------------------------------------------------
Total Charging Stations: {summary['total_stations']}
Total Connectors: {summary['total_connectors']}
Fast Chargers (DC): {summary['fast_chargers']} ({summary['fast_charger_ratio']}%)
Unique Operators: {summary['unique_operators']}
Operational Stations: {summary['operational_stations']}
Public Access: {summary['public_access']}

--------------------------------------------------------------------------------
COVERAGE ANALYSIS
--------------------------------------------------------------------------------
Area Analyzed: {coverage['area_sq_km']} sq km
Station Density: {coverage['station_density']} per sq km
Connector Density: {coverage['connector_density']} per sq km
Coverage Rating: {coverage['coverage_rating']} (Score: {coverage['coverage_score']}/5)
Distribution: {coverage['distribution_rating']}

--------------------------------------------------------------------------------
MARKET ANALYSIS
--------------------------------------------------------------------------------
Total Operators: {operators['total_operators']}
Top Operator: {operators['top_operator']}
Market Concentration: {operators['market_concentration']} (HHI: {operators['hhi_index']})

Top Operators by Market Share:
"""
        
        for name, data in list(operators['distribution'].items())[:5]:
            report += f"  - {name}: {data['stations']} stations ({data['market_share']}%)\n"
        
        report += f"""
--------------------------------------------------------------------------------
IDENTIFIED GAPS
--------------------------------------------------------------------------------
{analysis['gaps']['summary']}

================================================================================
"""
        return report


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🔌 Infrastructure Analyzer")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = InfrastructureAnalyzer()
    print("✅ Analyzer initialized")
    
    # Analyze San Francisco
    print("\n📍 Analyzing San Francisco EV infrastructure...")
    analysis = analyzer.analyze_location(
        latitude=37.7749,
        longitude=-122.4194,
        radius_km=10,
        location_name="San Francisco, CA"
    )
    
    if analysis["status"] == "success":
        print(f"\n✅ Analysis Complete!")
        print(f"   Stations: {analysis['summary']['total_stations']}")
        print(f"   Connectors: {analysis['summary']['total_connectors']}")
        print(f"   Fast Chargers: {analysis['summary']['fast_chargers']}")
        print(f"   Coverage: {analysis['coverage']['coverage_rating']}")
        print(f"   Top Operator: {analysis['operators']['top_operator']}")
        
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