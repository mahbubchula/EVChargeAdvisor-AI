"""
👥 US Census Bureau API Client
==============================

Fetches demographic data for equity analysis.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.base_api import BaseAPIClient, APIError
from config.api_keys import API_CONFIGS
from config.settings import CENSUS_SETTINGS


class CensusAPIClient(BaseAPIClient):
    """
    Client for US Census Bureau API.
    
    Provides access to demographic, economic, and housing data
    for equity and accessibility analysis.
    """
    
    # Variable codes and their meanings
    VARIABLES = {
        "B01003_001E": "total_population",
        "B19013_001E": "median_household_income",
        "B17001_002E": "population_below_poverty",
        "B17001_001E": "poverty_universe",
        "B25044_001E": "total_households_vehicles",
        "B25044_003E": "households_no_vehicle",
        "B02001_001E": "total_race",
        "B02001_002E": "white_alone",
        "B02001_003E": "black_alone",
        "B02001_005E": "asian_alone",
        "B03001_003E": "hispanic_latino"
    }
    
    # State FIPS codes
    STATE_FIPS = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
        "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
        "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
        "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
        "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
        "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
        "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
        "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
        "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
        "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
        "DC": "11"
    }
    
    def __init__(self):
        """Initialize Census API client."""
        config = API_CONFIGS["census"]
        super().__init__(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )
        self.year = CENSUS_SETTINGS["year"]
        self.dataset = CENSUS_SETTINGS["dataset"]
    
    def _add_auth_params(self, params: Dict) -> Dict:
        """Add API key to parameters."""
        if self.api_key:
            params["key"] = self.api_key
        return params
    
    def _build_url(self, year: int = None, dataset: str = None) -> str:
        """Build Census API URL."""
        y = year or self.year
        d = dataset or self.dataset
        return f"{self.base_url}/{y}/{d}"
    
    # =========================================================================
    # MAIN METHODS
    # =========================================================================
    
    def get_county_data(
        self,
        state_fips: str,
        county_fips: str = "*",
        variables: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get demographic data for county/counties.
        
        Args:
            state_fips: State FIPS code (e.g., "06" for California)
            county_fips: County FIPS code or "*" for all counties
            variables: List of variable codes to fetch
            
        Returns:
            List of county data dictionaries
        """
        if variables is None:
            variables = list(self.VARIABLES.keys())
        
        # Build request
        var_string = ",".join(["NAME"] + variables)
        
        params = {
            "get": var_string,
            "for": f"county:{county_fips}",
            "in": f"state:{state_fips}"
        }
        params = self._add_auth_params(params)
        
        try:
            # Census API returns raw array, not JSON object
            url = self._build_url()
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_census_response(data, variables)
            
        except Exception as e:
            print(f"❌ Census API Error: {e}")
            return []
    
    def get_tract_data(
        self,
        state_fips: str,
        county_fips: str,
        tract: str = "*",
        variables: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get demographic data for census tract(s).
        
        Args:
            state_fips: State FIPS code
            county_fips: County FIPS code
            tract: Tract code or "*" for all tracts
            variables: List of variable codes
            
        Returns:
            List of tract data dictionaries
        """
        if variables is None:
            variables = list(self.VARIABLES.keys())
        
        var_string = ",".join(["NAME"] + variables)
        
        params = {
            "get": var_string,
            "for": f"tract:{tract}",
            "in": f"state:{state_fips}&in=county:{county_fips}"
        }
        params = self._add_auth_params(params)
        
        try:
            url = self._build_url()
            
            # Manual URL construction for nested geography
            full_url = f"{url}?get={var_string}&for=tract:{tract}&in=state:{state_fips}&in=county:{county_fips}&key={self.api_key}"
            
            response = self.session.get(full_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_census_response(data, variables)
            
        except Exception as e:
            print(f"❌ Census API Error: {e}")
            return []
    
    def get_state_data(
        self,
        state_fips: str = "*",
        variables: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get demographic data for state(s).
        
        Args:
            state_fips: State FIPS code or "*" for all states
            variables: List of variable codes
            
        Returns:
            List of state data dictionaries
        """
        if variables is None:
            variables = list(self.VARIABLES.keys())
        
        var_string = ",".join(["NAME"] + variables)
        
        params = {
            "get": var_string,
            "for": f"state:{state_fips}"
        }
        params = self._add_auth_params(params)
        
        try:
            url = self._build_url()
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_census_response(data, variables)
            
        except Exception as e:
            print(f"❌ Census API Error: {e}")
            return []
    
    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================
    
    def get_demographics_by_state_abbr(
        self,
        state_abbr: str,
        county_fips: str = "*"
    ) -> List[Dict[str, Any]]:
        """
        Get demographics using state abbreviation.
        
        Args:
            state_abbr: State abbreviation (e.g., "CA", "NY")
            county_fips: County FIPS or "*" for all
            
        Returns:
            List of demographic data dictionaries
        """
        state_fips = self.STATE_FIPS.get(state_abbr.upper())
        if not state_fips:
            print(f"❌ Unknown state abbreviation: {state_abbr}")
            return []
        
        return self.get_county_data(state_fips, county_fips)
    
    def get_equity_metrics(
        self,
        state_fips: str,
        county_fips: str
    ) -> Dict[str, Any]:
        """
        Get key equity metrics for a county.
        
        Args:
            state_fips: State FIPS code
            county_fips: County FIPS code
            
        Returns:
            Dictionary with equity metrics
        """
        # Fetch specific equity-related variables
        variables = [
            "B01003_001E",  # Total population
            "B19013_001E",  # Median income
            "B17001_002E",  # Below poverty
            "B17001_001E",  # Poverty universe
            "B25044_001E",  # Total households (vehicles)
            "B25044_003E"   # No vehicle households
        ]
        
        data = self.get_county_data(state_fips, county_fips, variables)
        
        if not data:
            return {}
        
        county = data[0]
        
        # Calculate derived metrics
        poverty_rate = 0
        if county.get("poverty_universe") and county["poverty_universe"] > 0:
            poverty_rate = (county.get("population_below_poverty", 0) / county["poverty_universe"]) * 100
        
        no_vehicle_rate = 0
        if county.get("total_households_vehicles") and county["total_households_vehicles"] > 0:
            no_vehicle_rate = (county.get("households_no_vehicle", 0) / county["total_households_vehicles"]) * 100
        
        return {
            "name": county.get("name", "Unknown"),
            "population": county.get("total_population", 0),
            "median_income": county.get("median_household_income", 0),
            "poverty_rate": round(poverty_rate, 2),
            "no_vehicle_rate": round(no_vehicle_rate, 2),
            "raw_data": county
        }
    
    # =========================================================================
    # PARSING HELPERS
    # =========================================================================
    
    def _parse_census_response(
        self,
        data: List[List],
        variables: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Parse Census API response into list of dictionaries.
        
        Args:
            data: Raw Census API response (list of lists)
            variables: Variable codes requested
            
        Returns:
            List of parsed dictionaries
        """
        if not data or len(data) < 2:
            return []
        
        # First row is header
        header = data[0]
        results = []
        
        for row in data[1:]:
            record = {}
            for i, value in enumerate(row):
                col_name = header[i]
                
                # Map variable code to friendly name
                if col_name in self.VARIABLES:
                    friendly_name = self.VARIABLES[col_name]
                    # Convert to number if possible
                    try:
                        record[friendly_name] = int(value) if value else 0
                    except (ValueError, TypeError):
                        record[friendly_name] = value
                elif col_name == "NAME":
                    record["name"] = value
                else:
                    # Geographic identifiers (state, county, tract)
                    record[col_name.lower()] = value
            
            results.append(record)
        
        return results
    
    def get_fips_for_state(self, state_abbr: str) -> Optional[str]:
        """Get FIPS code for state abbreviation."""
        return self.STATE_FIPS.get(state_abbr.upper())


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("👥 US Census Bureau API Client")
    print("=" * 60)
    
    # Initialize client
    client = CensusAPIClient()
    print(f"✅ Client initialized: {client}")
    
    # Test: Get San Francisco County data (FIPS: 06-075)
    print("\n📍 Fetching San Francisco County demographics...")
    
    equity = client.get_equity_metrics(
        state_fips="06",  # California
        county_fips="075"  # San Francisco
    )
    
    if equity:
        print(f"✅ Data retrieved for: {equity['name']}")
        print(f"\n📊 Equity Metrics:")
        print(f"   Population: {equity['population']:,}")
        print(f"   Median Income: ${equity['median_income']:,}")
        print(f"   Poverty Rate: {equity['poverty_rate']}%")
        print(f"   No Vehicle Rate: {equity['no_vehicle_rate']}%")
    else:
        print("❌ No data found or API error")
    
    # Test: Get California state data
    print("\n📍 Fetching California state data...")
    state_data = client.get_demographics_by_state_abbr("CA", county_fips="*")
    
    if state_data:
        print(f"✅ Found {len(state_data)} counties in California")
        
        # Show first 3 counties
        print("\n📋 First 3 Counties:")
        for county in state_data[:3]:
            name = county.get("name", "Unknown")
            pop = county.get("total_population", 0)
            income = county.get("median_household_income", 0)
            print(f"   {name}: Pop {pop:,}, Income ${income:,}")
    else:
        print("❌ No state data found")
    
    # Show client stats
    print("\n📈 Client Stats:")
    print(f"   {client.get_stats()}")