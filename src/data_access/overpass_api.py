"""
🗺️ OpenStreetMap Overpass API Client
=====================================

Fetches POIs, amenities, and transit data for accessibility analysis.

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
from config.settings import OVERPASS_SETTINGS


class OverpassAPIClient(BaseAPIClient):
    """
    Client for OpenStreetMap Overpass API.
    
    Overpass API allows querying OpenStreetMap data for
    POIs, amenities, transit stops, and more.
    """
    
    # Amenity categories for convenience scoring
    AMENITY_CATEGORIES = {
        "dining": ["restaurant", "cafe", "fast_food", "food_court", "bar"],
        "shopping": ["supermarket", "convenience", "mall", "shop"],
        "services": ["bank", "atm", "pharmacy", "post_office"],
        "transit": ["bus_stop", "subway_entrance", "train_station", "tram_stop"],
        "parking": ["parking", "parking_entrance"],
        "healthcare": ["hospital", "clinic", "doctors", "dentist"],
        "entertainment": ["cinema", "theatre", "museum", "library"]
    }
    
    def __init__(self):
        """Initialize Overpass API client."""
        config = API_CONFIGS["overpass"]
        super().__init__(
            base_url=config["base_url"],
            api_key=config.get("api_key")  # No API key needed
        )
        self.settings = OVERPASS_SETTINGS
        self.timeout = self.settings.get("timeout", 60)
    
    def _add_auth_params(self, params: Dict) -> Dict:
        """No authentication needed for Overpass."""
        return params
    
    # =========================================================================
    # QUERY BUILDERS
    # =========================================================================
    
    def _build_amenity_query(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        amenity_types: List[str]
    ) -> str:
        """
        Build Overpass QL query for amenities.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_m: Search radius in meters
            amenity_types: List of amenity types to search
            
        Returns:
            Overpass QL query string
        """
        amenity_filter = "|".join(amenity_types)
        
        query = f"""
        [out:json][timeout:{self.timeout}];
        (
            node["amenity"~"{amenity_filter}"](around:{radius_m},{latitude},{longitude});
            way["amenity"~"{amenity_filter}"](around:{radius_m},{latitude},{longitude});
        );
        out center;
        """
        return query
    
    def _build_transit_query(
        self,
        latitude: float,
        longitude: float,
        radius_m: int
    ) -> str:
        """
        Build Overpass QL query for public transit.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_m: Search radius in meters
            
        Returns:
            Overpass QL query string
        """
        query = f"""
        [out:json][timeout:{self.timeout}];
        (
            node["highway"="bus_stop"](around:{radius_m},{latitude},{longitude});
            node["railway"="station"](around:{radius_m},{latitude},{longitude});
            node["railway"="subway_entrance"](around:{radius_m},{latitude},{longitude});
            node["railway"="tram_stop"](around:{radius_m},{latitude},{longitude});
            node["public_transport"="stop_position"](around:{radius_m},{latitude},{longitude});
            node["public_transport"="platform"](around:{radius_m},{latitude},{longitude});
        );
        out;
        """
        return query
    
    def _build_general_query(
        self,
        latitude: float,
        longitude: float,
        radius_m: int
    ) -> str:
        """
        Build Overpass QL query for general POIs.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_m: Search radius in meters
            
        Returns:
            Overpass QL query string
        """
        query = f"""
        [out:json][timeout:{self.timeout}];
        (
            node["amenity"](around:{radius_m},{latitude},{longitude});
            node["shop"](around:{radius_m},{latitude},{longitude});
            node["highway"="bus_stop"](around:{radius_m},{latitude},{longitude});
            node["railway"~"station|subway_entrance|tram_stop"](around:{radius_m},{latitude},{longitude});
        );
        out;
        """
        return query
    
    # =========================================================================
    # MAIN METHODS
    # =========================================================================
    
    def get_amenities(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 500,
        amenity_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get amenities near a location.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_m: Search radius in meters
            amenity_types: Specific amenity types (default: from settings)
            
        Returns:
            List of amenity dictionaries
        """
        if amenity_types is None:
            amenity_types = self.settings["amenity_types"]
        
        query = self._build_amenity_query(latitude, longitude, radius_m, amenity_types)
        
        try:
            response = self.session.post(
                self.base_url,
                data={"data": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            return self._parse_elements(data.get("elements", []))
            
        except Exception as e:
            print(f"❌ Overpass API Error: {e}")
            return []
    
    def get_transit_stops(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Get public transit stops near a location.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_m: Search radius in meters
            
        Returns:
            List of transit stop dictionaries
        """
        query = self._build_transit_query(latitude, longitude, radius_m)
        
        try:
            response = self.session.post(
                self.base_url,
                data={"data": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            return self._parse_elements(data.get("elements", []), is_transit=True)
            
        except Exception as e:
            print(f"❌ Overpass API Error: {e}")
            return []
    
    def get_all_pois(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 500
    ) -> Dict[str, List[Dict]]:
        """
        Get all POIs categorized by type.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_m: Search radius in meters
            
        Returns:
            Dictionary with categorized POIs
        """
        query = self._build_general_query(latitude, longitude, radius_m)
        
        try:
            response = self.session.post(
                self.base_url,
                data={"data": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            elements = data.get("elements", [])
            return self._categorize_elements(elements)
            
        except Exception as e:
            print(f"❌ Overpass API Error: {e}")
            return {}
    
    # =========================================================================
    # PARSING HELPERS
    # =========================================================================
    
    def _parse_elements(
        self,
        elements: List[Dict],
        is_transit: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Parse Overpass API elements into clean format.
        
        Args:
            elements: Raw elements from API
            is_transit: Whether these are transit elements
            
        Returns:
            List of parsed dictionaries
        """
        results = []
        
        for elem in elements:
            tags = elem.get("tags", {})
            
            # Get coordinates (handle ways with center)
            lat = elem.get("lat") or elem.get("center", {}).get("lat")
            lon = elem.get("lon") or elem.get("center", {}).get("lon")
            
            if not lat or not lon:
                continue
            
            parsed = {
                "id": elem.get("id"),
                "type": elem.get("type"),
                "name": tags.get("name", "Unnamed"),
                "latitude": lat,
                "longitude": lon,
                "amenity": tags.get("amenity"),
                "shop": tags.get("shop"),
                "tags": tags
            }
            
            if is_transit:
                parsed["transit_type"] = self._get_transit_type(tags)
                parsed["operator"] = tags.get("operator", "Unknown")
                parsed["network"] = tags.get("network", "")
            
            results.append(parsed)
        
        return results
    
    def _get_transit_type(self, tags: Dict) -> str:
        """Determine transit type from tags."""
        if tags.get("highway") == "bus_stop":
            return "bus_stop"
        if tags.get("railway") == "station":
            return "train_station"
        if tags.get("railway") == "subway_entrance":
            return "subway"
        if tags.get("railway") == "tram_stop":
            return "tram"
        if tags.get("public_transport"):
            return tags.get("public_transport")
        return "unknown"
    
    def _categorize_elements(self, elements: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize elements by type.
        
        Args:
            elements: Raw elements from API
            
        Returns:
            Dictionary with categorized elements
        """
        categories = {
            "dining": [],
            "shopping": [],
            "services": [],
            "transit": [],
            "healthcare": [],
            "entertainment": [],
            "other": []
        }
        
        for elem in elements:
            tags = elem.get("tags", {})
            amenity = tags.get("amenity", "")
            shop = tags.get("shop", "")
            highway = tags.get("highway", "")
            railway = tags.get("railway", "")
            
            # Get coordinates
            lat = elem.get("lat") or elem.get("center", {}).get("lat")
            lon = elem.get("lon") or elem.get("center", {}).get("lon")
            
            if not lat or not lon:
                continue
            
            parsed = {
                "id": elem.get("id"),
                "name": tags.get("name", "Unnamed"),
                "latitude": lat,
                "longitude": lon,
                "type": amenity or shop or highway or railway,
                "tags": tags
            }
            
            # Categorize
            if amenity in self.AMENITY_CATEGORIES["dining"]:
                categories["dining"].append(parsed)
            elif amenity in self.AMENITY_CATEGORIES["services"] or shop:
                categories["shopping" if shop else "services"].append(parsed)
            elif amenity in self.AMENITY_CATEGORIES["healthcare"]:
                categories["healthcare"].append(parsed)
            elif amenity in self.AMENITY_CATEGORIES["entertainment"]:
                categories["entertainment"].append(parsed)
            elif highway == "bus_stop" or railway:
                parsed["transit_type"] = highway or railway
                categories["transit"].append(parsed)
            else:
                categories["other"].append(parsed)
        
        return categories
    
    # =========================================================================
    # CONVENIENCE SCORING
    # =========================================================================
    
    def calculate_convenience_score(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 500
    ) -> Dict[str, Any]:
        """
        Calculate convenience score for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            radius_m: Search radius in meters
            
        Returns:
            Dictionary with scores and details
        """
        pois = self.get_all_pois(latitude, longitude, radius_m)
        
        # Count by category
        counts = {cat: len(items) for cat, items in pois.items()}
        
        # Calculate scores (0-10 scale)
        scores = {
            "dining": min(counts.get("dining", 0) * 0.5, 2.5),
            "shopping": min(counts.get("shopping", 0) * 0.3, 1.5),
            "services": min(counts.get("services", 0) * 0.3, 1.5),
            "transit": min(counts.get("transit", 0) * 0.5, 2.5),
            "healthcare": min(counts.get("healthcare", 0) * 0.5, 1.0),
            "entertainment": min(counts.get("entertainment", 0) * 0.5, 1.0)
        }
        
        total_score = sum(scores.values())
        
        return {
            "total_score": round(total_score, 1),
            "max_score": 10.0,
            "category_scores": scores,
            "category_counts": counts,
            "total_pois": sum(counts.values()),
            "grade": self._get_grade(total_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 8.5:
            return "A"
        elif score >= 7.0:
            return "B"
        elif score >= 5.0:
            return "C"
        elif score >= 3.0:
            return "D"
        else:
            return "F"


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🗺️ OpenStreetMap Overpass API Client")
    print("=" * 60)
    
    # Initialize client
    client = OverpassAPIClient()
    print(f"✅ Client initialized: {client}")
    
    # Test: Get POIs near a San Francisco charging station
    print("\n📍 Fetching POIs near San Francisco (37.7749, -122.4194)...")
    
    pois = client.get_all_pois(
        latitude=37.7749,
        longitude=-122.4194,
        radius_m=500
    )
    
    if pois:
        print("✅ POIs retrieved!")
        print("\n📊 POI Counts by Category:")
        for category, items in pois.items():
            print(f"   {category.capitalize()}: {len(items)}")
    else:
        print("❌ No POIs found or API error")
    
    # Test: Calculate convenience score
    print("\n📍 Calculating convenience score...")
    score = client.calculate_convenience_score(
        latitude=37.7749,
        longitude=-122.4194,
        radius_m=500
    )
    
    if score:
        print(f"✅ Convenience Score: {score['total_score']}/10 (Grade: {score['grade']})")
        print("\n📋 Category Scores:")
        for cat, val in score['category_scores'].items():
            print(f"   {cat.capitalize()}: {val:.1f}")
    
    # Test: Get transit stops
    print("\n📍 Fetching transit stops...")
    transit = client.get_transit_stops(
        latitude=37.7749,
        longitude=-122.4194,
        radius_m=500
    )
    
    if transit:
        print(f"✅ Found {len(transit)} transit stops")
        # Show first 3
        for stop in transit[:3]:
            print(f"   - {stop['name']} ({stop.get('transit_type', 'unknown')})")
    else:
        print("⚠️ No transit stops found nearby")