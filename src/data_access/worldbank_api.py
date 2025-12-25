"""
🌍 World Bank API Client
========================

Fetches global demographic data for equity analysis worldwide.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.base_api import BaseAPIClient, APIError


class WorldBankAPIClient(BaseAPIClient):
    """
    Client for World Bank Open Data API.
    
    Provides global demographic and economic data for
    equity analysis in any country.
    
    Free, no API key required!
    """
    
    # Key indicators we use
    INDICATORS = {
        "SP.POP.TOTL": "total_population",
        "NY.GDP.PCAP.CD": "gdp_per_capita",
        "SI.POV.NAHC": "poverty_rate_national",
        "SI.POV.DDAY": "poverty_rate_extreme",
        "SP.URB.TOTL.IN.ZS": "urban_population_percent",
        "EG.ELC.ACCS.ZS": "electricity_access_percent",
        "IS.VEH.NVEH.P3": "vehicles_per_1000",
        "EN.ATM.CO2E.PC": "co2_emissions_per_capita",
        "NY.GNP.PCAP.CD": "gni_per_capita"
    }
    
    # Country codes mapping (common countries)
    COUNTRY_CODES = {
        # North America
        "united states": "USA", "usa": "USA", "us": "USA",
        "canada": "CAN", "mexico": "MEX",
        
        # Europe
        "united kingdom": "GBR", "uk": "GBR", "england": "GBR",
        "germany": "DEU", "france": "FRA", "italy": "ITA",
        "spain": "ESP", "netherlands": "NLD", "belgium": "BEL",
        "switzerland": "CHE", "austria": "AUT", "sweden": "SWE",
        "norway": "NOR", "denmark": "DNK", "finland": "FIN",
        "portugal": "PRT", "ireland": "IRL", "poland": "POL",
        
        # Asia
        "china": "CHN", "japan": "JPN", "south korea": "KOR", "korea": "KOR",
        "india": "IND", "indonesia": "IDN", "thailand": "THA",
        "vietnam": "VNM", "malaysia": "MYS", "singapore": "SGP",
        "philippines": "PHL", "taiwan": "TWN", "hong kong": "HKG",
        "bangladesh": "BGD", "pakistan": "PAK", "sri lanka": "LKA",
        
        # Middle East
        "saudi arabia": "SAU", "uae": "ARE", "united arab emirates": "ARE",
        "israel": "ISR", "turkey": "TUR", "iran": "IRN",
        
        # Oceania
        "australia": "AUS", "new zealand": "NZL",
        
        # South America
        "brazil": "BRA", "argentina": "ARG", "chile": "CHL",
        "colombia": "COL", "peru": "PER", "venezuela": "VEN",
        
        # Africa
        "south africa": "ZAF", "egypt": "EGY", "nigeria": "NGA",
        "kenya": "KEN", "morocco": "MAR", "ethiopia": "ETH"
    }
    
    def __init__(self):
        """Initialize World Bank API client."""
        super().__init__(
            base_url="https://api.worldbank.org/v2",
            api_key=None  # No API key needed!
        )
        self.cache_duration = 86400  # 24 hours (data doesn't change often)
    
    def _add_auth_params(self, params: Dict) -> Dict:
        """No authentication needed."""
        return params
    
    # =========================================================================
    # MAIN METHODS
    # =========================================================================
    
    def get_country_data(
        self,
        country_code: str,
        indicators: List[str] = None,
        year: int = None
    ) -> Dict[str, Any]:
        """
        Get demographic/economic data for a country.
        
        Args:
            country_code: ISO 3-letter country code (e.g., "USA", "THA", "GBR")
            indicators: List of indicator codes (default: all key indicators)
            year: Specific year (default: most recent)
            
        Returns:
            Dictionary with country data
        """
        if indicators is None:
            indicators = list(self.INDICATORS.keys())
        
        country_code = country_code.upper()
        
        result = {
            "country_code": country_code,
            "country_name": "",
            "year": year or "latest",
            "data": {}
        }
        
        for indicator in indicators:
            try:
                # Build URL
                endpoint = f"country/{country_code}/indicator/{indicator}"
                params = {
                    "format": "json",
                    "per_page": 10,  # Get recent years
                    "date": f"{year}:{year}" if year else None
                }
                # Remove None params
                params = {k: v for k, v in params.items() if v is not None}
                
                response = self.get(endpoint, params=params)
                
                # Parse response
                if isinstance(response, list) and len(response) > 1:
                    data_list = response[1]
                    if data_list and len(data_list) > 0:
                        # Get most recent non-null value
                        for entry in data_list:
                            if entry.get("value") is not None:
                                friendly_name = self.INDICATORS.get(indicator, indicator)
                                result["data"][friendly_name] = entry["value"]
                                result["country_name"] = entry.get("country", {}).get("value", "")
                                if not year:
                                    result["year"] = entry.get("date", "")
                                break
                                
            except Exception as e:
                print(f"⚠️ Failed to fetch {indicator}: {e}")
                continue
        
        return result
    
    def get_country_profile(self, country_code: str) -> Dict[str, Any]:
        """
        Get comprehensive country profile for equity analysis.
        
        Args:
            country_code: ISO country code
            
        Returns:
            Country profile dictionary
        """
        data = self.get_country_data(country_code)
        
        if not data.get("data"):
            return {"status": "error", "message": "No data available"}
        
        raw = data["data"]
        
        # Calculate derived metrics
        population = raw.get("total_population", 0)
        gdp_pc = raw.get("gdp_per_capita", 0)
        poverty = raw.get("poverty_rate_national") or raw.get("poverty_rate_extreme", 0)
        urban = raw.get("urban_population_percent", 50)
        vehicles = raw.get("vehicles_per_1000", 0)
        
        # Determine income level
        if gdp_pc >= 40000:
            income_level = "High Income"
        elif gdp_pc >= 12000:
            income_level = "Upper Middle Income"
        elif gdp_pc >= 4000:
            income_level = "Lower Middle Income"
        else:
            income_level = "Low Income"
        
        # EV readiness score (simplified)
        ev_readiness = min(100, (
            (raw.get("electricity_access_percent", 0) or 0) * 0.3 +
            min(gdp_pc / 500, 40) +
            (urban or 0) * 0.3
        ))
        
        return {
            "status": "success",
            "country_code": country_code,
            "country_name": data.get("country_name", "Unknown"),
            "year": data.get("year", "N/A"),
            "demographics": {
                "population": int(population) if population else 0,
                "urban_percent": round(urban, 1) if urban else 0,
                "vehicles_per_1000": round(vehicles, 1) if vehicles else 0
            },
            "economics": {
                "gdp_per_capita": round(gdp_pc, 0) if gdp_pc else 0,
                "gni_per_capita": round(raw.get("gni_per_capita", 0) or 0, 0),
                "income_level": income_level,
                "poverty_rate": round(poverty, 1) if poverty else None
            },
            "infrastructure": {
                "electricity_access": round(raw.get("electricity_access_percent", 0) or 0, 1),
                "ev_readiness_score": round(ev_readiness, 1)
            },
            "environment": {
                "co2_per_capita": round(raw.get("co2_emissions_per_capita", 0) or 0, 2)
            },
            "raw_data": raw
        }
    
    def get_country_code(self, country_name: str) -> Optional[str]:
        """
        Get ISO country code from country name.
        
        Args:
            country_name: Country name (case-insensitive)
            
        Returns:
            ISO 3-letter code or None
        """
        name_lower = country_name.lower().strip()
        return self.COUNTRY_CODES.get(name_lower)
    
    def search_country(self, query: str) -> List[Dict[str, str]]:
        """
        Search for countries matching a query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching countries
        """
        query_lower = query.lower()
        matches = []
        
        for name, code in self.COUNTRY_CODES.items():
            if query_lower in name:
                matches.append({"name": name.title(), "code": code})
        
        return matches
    
    # =========================================================================
    # COMPARISON METHODS
    # =========================================================================
    
    def compare_countries(
        self,
        country_codes: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple countries.
        
        Args:
            country_codes: List of ISO country codes
            
        Returns:
            Comparison dictionary
        """
        profiles = {}
        
        for code in country_codes:
            profile = self.get_country_profile(code)
            if profile.get("status") == "success":
                profiles[code] = profile
        
        if not profiles:
            return {"status": "error", "message": "No data for any country"}
        
        return {
            "status": "success",
            "countries": profiles,
            "comparison": self._generate_comparison(profiles)
        }
    
    def _generate_comparison(self, profiles: Dict) -> Dict[str, Any]:
        """Generate comparison metrics."""
        gdps = [(c, p["economics"]["gdp_per_capita"]) for c, p in profiles.items()]
        pops = [(c, p["demographics"]["population"]) for c, p in profiles.items()]
        evs = [(c, p["infrastructure"]["ev_readiness_score"]) for c, p in profiles.items()]
        
        return {
            "highest_gdp": max(gdps, key=lambda x: x[1]) if gdps else None,
            "largest_population": max(pops, key=lambda x: x[1]) if pops else None,
            "highest_ev_readiness": max(evs, key=lambda x: x[1]) if evs else None
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🌍 World Bank API Client")
    print("=" * 60)
    
    # Initialize client
    client = WorldBankAPIClient()
    print("✅ Client initialized (No API key needed!)")
    
    # Test: Get Thailand data
    print("\n📍 Fetching Thailand country profile...")
    thailand = client.get_country_profile("THA")
    
    if thailand.get("status") == "success":
        print(f"✅ Data retrieved for: {thailand['country_name']}")
        print(f"\n📊 Demographics:")
        print(f"   Population: {thailand['demographics']['population']:,}")
        print(f"   Urban: {thailand['demographics']['urban_percent']}%")
        print(f"   Vehicles/1000: {thailand['demographics']['vehicles_per_1000']}")
        print(f"\n💰 Economics:")
        print(f"   GDP per Capita: ${thailand['economics']['gdp_per_capita']:,}")
        print(f"   Income Level: {thailand['economics']['income_level']}")
        print(f"   Poverty Rate: {thailand['economics']['poverty_rate']}%")
        print(f"\n⚡ Infrastructure:")
        print(f"   Electricity Access: {thailand['infrastructure']['electricity_access']}%")
        print(f"   EV Readiness Score: {thailand['infrastructure']['ev_readiness_score']}/100")
    
    # Test: Get UK data
    print("\n" + "=" * 60)
    print("📍 Fetching United Kingdom country profile...")
    uk = client.get_country_profile("GBR")
    
    if uk.get("status") == "success":
        print(f"✅ {uk['country_name']}")
        print(f"   Population: {uk['demographics']['population']:,}")
        print(f"   GDP/Capita: ${uk['economics']['gdp_per_capita']:,}")
        print(f"   EV Readiness: {uk['infrastructure']['ev_readiness_score']}/100")
    
    # Test: Compare countries
    print("\n" + "=" * 60)
    print("📍 Comparing USA, Germany, Japan, Thailand...")
    comparison = client.compare_countries(["USA", "DEU", "JPN", "THA"])
    
    if comparison.get("status") == "success":
        print("✅ Comparison complete!")
        print(f"   Highest GDP: {comparison['comparison']['highest_gdp']}")
        print(f"   Largest Population: {comparison['comparison']['largest_population']}")
        print(f"   Best EV Readiness: {comparison['comparison']['highest_ev_readiness']}")
    
    print("\n✅ World Bank API working globally!")