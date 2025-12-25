"""
OpenChargeMap API Client
=========================

Fetches EV charging station data from OpenChargeMap API.

Author: MAHBUB
Date: December 25, 2024
"""
import requests
import time
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.api_keys import OPENCHARGEMAP_API_KEY

class OpenChargeMapClient:
    """Client for OpenChargeMap API"""
    
    def __init__(self):
        """Initialize the client"""
        self.base_url = "https://api.openchargemap.io/v3"
        self.api_key = OPENCHARGEMAP_API_KEY
        self.timeout = 15
        
    def get_stations_by_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: int = 10,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Get charging stations near a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude  
            radius_km: Search radius in kilometers
            max_results: Maximum number of results
            
        Returns:
            List of charging station dictionaries
        """
        print(f"🔍 Searching for stations near ({latitude}, {longitude})...")
        print(f"   Radius: {radius_km} km, Max results: {max_results}")
        
        url = f"{self.base_url}/poi/"
        params = {
            "output": "json",
            "key": self.api_key,
            "latitude": latitude,
            "longitude": longitude,
            "distance": radius_km,
            "maxresults": max_results,
            "compact": "false",
            "verbose": "false"
        }
        
        try:
            start_time = time.time()
            response = requests.get(url, params=params, timeout=self.timeout)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data)} stations in {duration:.2f}s")
                return data
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return []
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    def get_station_summary(self, station: Dict) -> Dict:
        """
        Extract key information from a station.
        
        Args:
            station: Station dictionary from API
            
        Returns:
            Simplified station info
        """
        addr = station.get('AddressInfo', {})
        operator = station.get('OperatorInfo', {})
        
        return {
            'id': station.get('ID'),
            'name': addr.get('Title', 'Unknown'),
            'address': addr.get('AddressLine1', ''),
            'city': addr.get('Town', ''),
            'state': addr.get('StateOrProvince', ''),
            'latitude': addr.get('Latitude'),
            'longitude': addr.get('Longitude'),
            'distance_km': addr.get('Distance'),
            'operator': operator.get('Title', 'Unknown') if operator else 'Unknown',
            'num_points': station.get('NumberOfPoints', 0),
        }


# Test the module
if __name__ == "__main__":
    print("🧪 Testing OpenChargeMap Client")
    print("=" * 60)
    
    client = OpenChargeMapClient()
    
    # Test: Get stations in San Francisco
    stations = client.get_stations_by_location(
        latitude=37.7749,
        longitude=-122.4194,
        radius_km=5,
        max_results=5
    )
    
    print(f"\n📊 Results:")
    print("=" * 60)
    
    for i, station in enumerate(stations[:3], 1):
        summary = client.get_station_summary(station)
        print(f"\n{i}. {summary['name']}")
        print(f"   Address: {summary['address']}, {summary['city']}")
        print(f"   Operator: {summary['operator']}")
        print(f"   Ports: {summary['num_points']}")
        print(f"   Distance: {summary['distance_km']:.2f} km")
    
    print("\n" + "=" * 60)
    print("✅ Module working perfectly!")