"""
🔌 OpenChargeMap API Client
===========================

Fetches EV charging station data from OpenChargeMap.

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
from config.settings import OPENCHARGE_SETTINGS


class OpenChargeMapClient(BaseAPIClient):
    """
    Client for OpenChargeMap API.
    
    OpenChargeMap is the world's largest open database of 
    EV charging stations with 200,000+ locations globally.
    """
    
    def __init__(self):
        """Initialize OpenChargeMap client."""
        config = API_CONFIGS["openchargemap"]
        super().__init__(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )
        self.settings = OPENCHARGE_SETTINGS
    
    def _add_auth_params(self, params: Dict) -> Dict:
        """Add API key to parameters."""
        if self.api_key:
            params["key"] = self.api_key
        return params
    
    # =========================================================================
    # MAIN METHODS
    # =========================================================================
    
    def get_stations_by_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        max_results: int = 100,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Get charging stations near a location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_km: Search radius in kilometers
            max_results: Maximum number of results
            **filters: Additional filters (operator_id, level_id, etc.)
            
        Returns:
            List of charging station dictionaries
        """
        params = {
            "output": "json",
            "latitude": latitude,
            "longitude": longitude,
            "distance": radius_km,
            "distanceunit": "KM",
            "maxresults": min(max_results, self.settings["max_results"]),
            "compact": self.settings["compact"],
            "verbose": self.settings["verbose"]
        }
        
        # Add optional filters
        if filters.get("operator_id"):
            params["operatorid"] = filters["operator_id"]
        if filters.get("level_id"):
            params["levelid"] = filters["level_id"]
        if filters.get("connection_type_id"):
            params["connectiontypeid"] = filters["connection_type_id"]
        if filters.get("country_code"):
            params["countrycode"] = filters["country_code"]
        if filters.get("status_type_id"):
            params["statustypeid"] = filters["status_type_id"]
        
        # Add authentication
        params = self._add_auth_params(params)
        
        try:
            response = self.get("poi/", params=params)
            return response if isinstance(response, list) else []
        except APIError as e:
            print(f"❌ OpenChargeMap Error: {e.message}")
            return []
    
    def get_stations_by_country(
        self,
        country_code: str,
        max_results: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Get charging stations by country.
        
        Args:
            country_code: ISO country code (e.g., "US", "UK", "TH")
            max_results: Maximum number of results
            
        Returns:
            List of charging station dictionaries
        """
        params = {
            "output": "json",
            "countrycode": country_code.upper(),
            "maxresults": min(max_results, self.settings["max_results"]),
            "compact": self.settings["compact"],
            "verbose": self.settings["verbose"]
        }
        
        params = self._add_auth_params(params)
        
        try:
            response = self.get("poi/", params=params)
            return response if isinstance(response, list) else []
        except APIError as e:
            print(f"❌ OpenChargeMap Error: {e.message}")
            return []
    
    def get_stations_by_city(
        self,
        city: str,
        country_code: str = "US",
        max_results: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Get charging stations by city name.
        
        Args:
            city: City name
            country_code: ISO country code
            max_results: Maximum number of results
            
        Returns:
            List of charging station dictionaries
        """
        # Use geocoding from address
        params = {
            "output": "json",
            "countrycode": country_code.upper(),
            "maxresults": min(max_results, self.settings["max_results"]),
            "compact": self.settings["compact"],
            "verbose": self.settings["verbose"]
        }
        
        params = self._add_auth_params(params)
        
        try:
            response = self.get("poi/", params=params)
            stations = response if isinstance(response, list) else []
            
            # Filter by city name
            city_lower = city.lower()
            filtered = [
                s for s in stations
                if s.get("AddressInfo", {}).get("Town", "").lower() == city_lower
            ]
            
            return filtered if filtered else stations[:max_results]
        except APIError as e:
            print(f"❌ OpenChargeMap Error: {e.message}")
            return []
    
    def get_station_by_id(self, station_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific charging station by ID.
        
        Args:
            station_id: OpenChargeMap station ID
            
        Returns:
            Station dictionary or None
        """
        params = {
            "output": "json",
            "chargepointid": station_id
        }
        
        params = self._add_auth_params(params)
        
        try:
            response = self.get("poi/", params=params)
            if isinstance(response, list) and len(response) > 0:
                return response[0]
            return None
        except APIError as e:
            print(f"❌ OpenChargeMap Error: {e.message}")
            return None
    
    def get_reference_data(self) -> Dict[str, Any]:
        """
        Get reference data (operators, connection types, etc.).
        
        Returns:
            Dictionary containing reference data
        """
        params = {"output": "json"}
        params = self._add_auth_params(params)
        
        try:
            return self.get("referencedata/", params=params)
        except APIError as e:
            print(f"❌ OpenChargeMap Error: {e.message}")
            return {}
    
    # =========================================================================
    # DATA PARSING HELPERS
    # =========================================================================
    
    @staticmethod
    def parse_station(station: Dict) -> Dict[str, Any]:
        """
        Parse raw station data into clean format.
        
        Args:
            station: Raw station dictionary from API
            
        Returns:
            Cleaned station dictionary
        """
        address = station.get("AddressInfo", {})
        operator = station.get("OperatorInfo") or {}
        connections = station.get("Connections", [])
        status = station.get("StatusType") or {}
        usage = station.get("UsageType") or {}
        
        # Parse connections
        parsed_connections = []
        total_power = 0
        for conn in connections:
            conn_type = conn.get("ConnectionType") or {}
            level = conn.get("Level") or {}
            power = conn.get("PowerKW") or 0
            total_power += power
            
            parsed_connections.append({
                "type": conn_type.get("Title", "Unknown"),
                "level": level.get("Title", "Unknown"),
                "power_kw": power,
                "quantity": conn.get("Quantity", 1),
                "is_fast_charge": level.get("IsFastChargeCapable", False)
            })
        
        return {
            "id": station.get("ID"),
            "uuid": station.get("UUID"),
            "name": address.get("Title", "Unknown Station"),
            "address": {
                "line1": address.get("AddressLine1", ""),
                "line2": address.get("AddressLine2", ""),
                "city": address.get("Town", ""),
                "state": address.get("StateOrProvince", ""),
                "postcode": address.get("Postcode", ""),
                "country": address.get("Country", {}).get("Title", "")
            },
            "location": {
                "latitude": address.get("Latitude"),
                "longitude": address.get("Longitude")
            },
            "operator": {
                "id": operator.get("ID"),
                "name": operator.get("Title", "Unknown"),
                "website": operator.get("WebsiteURL", ""),
                "is_private": operator.get("IsPrivateIndividual", False)
            },
            "connections": parsed_connections,
            "total_power_kw": total_power,
            "num_points": station.get("NumberOfPoints", len(connections)),
            "status": {
                "is_operational": status.get("IsOperational", True),
                "title": status.get("Title", "Unknown")
            },
            "usage": {
                "is_public": usage.get("IsPublicAccess", True),
                "is_pay_at_location": usage.get("IsPayAtLocation", False),
                "is_membership_required": usage.get("IsMembershipRequired", False),
                "title": usage.get("Title", "Unknown")
            },
            "date_last_verified": station.get("DateLastVerified"),
            "date_created": station.get("DateCreated")
        }
    
    def get_parsed_stations(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get charging stations and return parsed/cleaned data.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_km: Search radius in kilometers
            max_results: Maximum number of results
            
        Returns:
            List of parsed station dictionaries
        """
        raw_stations = self.get_stations_by_location(
            latitude, longitude, radius_km, max_results
        )
        return [self.parse_station(s) for s in raw_stations]
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_station_statistics(self, stations: List[Dict]) -> Dict[str, Any]:
        """
        Calculate statistics for a list of stations.
        
        Args:
            stations: List of parsed station dictionaries
            
        Returns:
            Statistics dictionary
        """
        if not stations:
            return {"total": 0}
        
        # Operator distribution
        operators = {}
        for s in stations:
            op_name = s.get("operator", {}).get("name", "Unknown")
            operators[op_name] = operators.get(op_name, 0) + 1
        
        # Connection types
        conn_types = {}
        total_connectors = 0
        fast_chargers = 0
        for s in stations:
            for conn in s.get("connections", []):
                conn_type = conn.get("type", "Unknown")
                qty = conn.get("quantity", 1)
                conn_types[conn_type] = conn_types.get(conn_type, 0) + qty
                total_connectors += qty
                if conn.get("is_fast_charge"):
                    fast_chargers += qty
        
        # Power statistics
        powers = [s.get("total_power_kw", 0) for s in stations if s.get("total_power_kw")]
        
        return {
            "total_stations": len(stations),
            "total_connectors": total_connectors,
            "fast_chargers": fast_chargers,
            "operators": operators,
            "connection_types": conn_types,
            "power_stats": {
                "min_kw": min(powers) if powers else 0,
                "max_kw": max(powers) if powers else 0,
                "avg_kw": sum(powers) / len(powers) if powers else 0
            },
            "operational": sum(1 for s in stations if s.get("status", {}).get("is_operational", True)),
            "public_access": sum(1 for s in stations if s.get("usage", {}).get("is_public", True))
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🔌 OpenChargeMap API Client")
    print("=" * 60)
    
    # Initialize client
    client = OpenChargeMapClient()
    print(f"✅ Client initialized: {client}")
    
    # Test: Get stations in San Francisco
    print("\n📍 Fetching stations near San Francisco...")
    stations = client.get_parsed_stations(
        latitude=37.7749,
        longitude=-122.4194,
        radius_km=10,
        max_results=20
    )
    
    if stations:
        print(f"✅ Found {len(stations)} charging stations!")
        
        # Show first station
        print("\n📋 First Station:")
        first = stations[0]
        print(f"   Name: {first['name']}")
        print(f"   City: {first['address']['city']}")
        print(f"   Operator: {first['operator']['name']}")
        print(f"   Connectors: {first['num_points']}")
        print(f"   Total Power: {first['total_power_kw']} kW")
        
        # Show statistics
        print("\n📊 Statistics:")
        stats = client.get_station_statistics(stations)
        print(f"   Total Stations: {stats['total_stations']}")
        print(f"   Total Connectors: {stats['total_connectors']}")
        print(f"   Fast Chargers: {stats['fast_chargers']}")
        print(f"   Operators: {len(stats['operators'])}")
    else:
        print("❌ No stations found or API error")
    
    # Show client stats
    print("\n📈 Client Stats:")
    print(f"   {client.get_stats()}")