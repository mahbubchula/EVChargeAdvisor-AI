"""
🗺️ Map Visualizer
==================

Creates interactive maps for EV charging infrastructure visualization.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional
import folium
from folium import plugins

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import MAP_SETTINGS, CHART_COLORS


class MapVisualizer:
    """
    Creates interactive maps for EV charging visualization.
    
    Features:
    - Station markers with popups
    - Heatmaps
    - Cluster maps
    - Coverage circles
    - Color-coded by operator/status
    """
    
    def __init__(self):
        """Initialize map visualizer."""
        self.settings = MAP_SETTINGS
        self.colors = CHART_COLORS
        
        # Operator colors
        self.operator_colors = {
            "ChargePoint": "#FF6B35",
            "Tesla": "#E82127",
            "EVgo": "#00A94F",
            "Electrify America": "#00264C",
            "Blink": "#00BFFF",
            "Shell Recharge": "#FBCE07",
            "default": "#3b82f6"
        }
        
        # Charging level colors
        self.level_colors = {
            "Level 1": "#94a3b8",
            "Level 2": "#3b82f6",
            "Level 3": "#10b981",
            "DC Fast": "#f59e0b"
        }
    
    # =========================================================================
    # MAIN MAP METHODS
    # =========================================================================
    
    def create_station_map(
        self,
        stations: List[Dict],
        center: tuple = None,
        zoom: int = None,
        title: str = "EV Charging Stations"
    ) -> folium.Map:
        """
        Create interactive map with charging station markers.
        
        Args:
            stations: List of parsed station dictionaries
            center: (lat, lon) tuple for map center
            zoom: Initial zoom level
            title: Map title
            
        Returns:
            Folium map object
        """
        if not stations:
            # Return empty map centered on US
            return folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        
        # Calculate center if not provided
        if center is None:
            lats = [s["location"]["latitude"] for s in stations if s.get("location")]
            lons = [s["location"]["longitude"] for s in stations if s.get("location")]
            center = (sum(lats) / len(lats), sum(lons) / len(lons))
        
        zoom = zoom or self.settings["default_zoom"]
        
        # Create map
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=self.settings["tile_provider"]
        )
        
        # Add markers for each station
        for station in stations:
            self._add_station_marker(m, station)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_cluster_map(
        self,
        stations: List[Dict],
        center: tuple = None,
        zoom: int = None
    ) -> folium.Map:
        """
        Create map with clustered markers for many stations.
        
        Args:
            stations: List of station dictionaries
            center: Map center
            zoom: Zoom level
            
        Returns:
            Folium map with marker clusters
        """
        if not stations:
            return folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        
        # Calculate center
        if center is None:
            lats = [s["location"]["latitude"] for s in stations if s.get("location")]
            lons = [s["location"]["longitude"] for s in stations if s.get("location")]
            center = (sum(lats) / len(lats), sum(lons) / len(lons))
        
        zoom = zoom or self.settings["default_zoom"]
        
        # Create map
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=self.settings["tile_provider"]
        )
        
        # Create marker cluster
        marker_cluster = plugins.MarkerCluster(name="Charging Stations")
        
        for station in stations:
            loc = station.get("location", {})
            lat, lon = loc.get("latitude"), loc.get("longitude")
            
            if lat and lon:
                popup_html = self._create_popup_html(station)
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=self._get_station_icon(station)
                ).add_to(marker_cluster)
        
        marker_cluster.add_to(m)
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_heatmap(
        self,
        stations: List[Dict],
        center: tuple = None,
        zoom: int = None,
        radius: int = 15
    ) -> folium.Map:
        """
        Create heatmap showing station density.
        
        Args:
            stations: List of station dictionaries
            center: Map center
            zoom: Zoom level
            radius: Heatmap point radius
            
        Returns:
            Folium map with heatmap layer
        """
        if not stations:
            return folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        
        # Get coordinates
        heat_data = []
        for station in stations:
            loc = station.get("location", {})
            lat, lon = loc.get("latitude"), loc.get("longitude")
            if lat and lon:
                # Weight by number of connectors
                weight = station.get("num_points", 1)
                heat_data.append([lat, lon, weight])
        
        # Calculate center
        if center is None:
            lats = [d[0] for d in heat_data]
            lons = [d[1] for d in heat_data]
            center = (sum(lats) / len(lats), sum(lons) / len(lons))
        
        zoom = zoom or self.settings["default_zoom"]
        
        # Create map
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=self.settings["tile_provider"]
        )
        
        # Add heatmap
        plugins.HeatMap(
            heat_data,
            radius=radius,
            blur=10,
            max_zoom=18,
            name="Station Density"
        ).add_to(m)
        
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_operator_map(
        self,
        stations: List[Dict],
        center: tuple = None,
        zoom: int = None
    ) -> folium.Map:
        """
        Create map with stations colored by operator.
        
        Args:
            stations: List of station dictionaries
            center: Map center
            zoom: Zoom level
            
        Returns:
            Folium map with operator-colored markers
        """
        if not stations:
            return folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        
        # Calculate center
        if center is None:
            lats = [s["location"]["latitude"] for s in stations if s.get("location")]
            lons = [s["location"]["longitude"] for s in stations if s.get("location")]
            center = (sum(lats) / len(lats), sum(lons) / len(lons))
        
        zoom = zoom or self.settings["default_zoom"]
        
        # Create map
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=self.settings["tile_provider"]
        )
        
        # Group stations by operator
        operators = {}
        for station in stations:
            op_name = station.get("operator", {}).get("name", "Unknown")
            if op_name not in operators:
                operators[op_name] = []
            operators[op_name].append(station)
        
        # Create feature group for each operator
        for op_name, op_stations in operators.items():
            fg = folium.FeatureGroup(name=f"{op_name} ({len(op_stations)})")
            
            color = self._get_operator_color(op_name)
            
            for station in op_stations:
                loc = station.get("location", {})
                lat, lon = loc.get("latitude"), loc.get("longitude")
                
                if lat and lon:
                    popup_html = self._create_popup_html(station)
                    
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=8,
                        popup=folium.Popup(popup_html, max_width=300),
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7
                    ).add_to(fg)
            
            fg.add_to(m)
        
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_coverage_map(
        self,
        stations: List[Dict],
        coverage_radius_km: float = 2,
        center: tuple = None,
        zoom: int = None
    ) -> folium.Map:
        """
        Create map showing coverage radius around each station.
        
        Args:
            stations: List of station dictionaries
            coverage_radius_km: Coverage radius in km
            center: Map center
            zoom: Zoom level
            
        Returns:
            Folium map with coverage circles
        """
        if not stations:
            return folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        
        # Calculate center
        if center is None:
            lats = [s["location"]["latitude"] for s in stations if s.get("location")]
            lons = [s["location"]["longitude"] for s in stations if s.get("location")]
            center = (sum(lats) / len(lats), sum(lons) / len(lons))
        
        zoom = zoom or self.settings["default_zoom"] - 1
        
        # Create map
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=self.settings["tile_provider"]
        )
        
        # Add coverage circles
        coverage_group = folium.FeatureGroup(name="Coverage Area")
        
        for station in stations:
            loc = station.get("location", {})
            lat, lon = loc.get("latitude"), loc.get("longitude")
            
            if lat and lon:
                # Coverage circle
                folium.Circle(
                    location=[lat, lon],
                    radius=coverage_radius_km * 1000,  # Convert to meters
                    color="#3b82f6",
                    fill=True,
                    fill_color="#3b82f6",
                    fill_opacity=0.1,
                    weight=1
                ).add_to(coverage_group)
                
                # Station marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color="#ef4444",
                    fill=True,
                    fill_color="#ef4444",
                    fill_opacity=0.8
                ).add_to(coverage_group)
        
        coverage_group.add_to(m)
        folium.LayerControl().add_to(m)
        
        return m
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _add_station_marker(self, map_obj: folium.Map, station: Dict) -> None:
        """Add a single station marker to the map."""
        loc = station.get("location", {})
        lat, lon = loc.get("latitude"), loc.get("longitude")
        
        if not lat or not lon:
            return
        
        popup_html = self._create_popup_html(station)
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=self._get_station_icon(station),
            tooltip=station.get("name", "Charging Station")
        ).add_to(map_obj)
    
    def _create_popup_html(self, station: Dict) -> str:
        """Create HTML content for station popup."""
        name = station.get("name", "Unknown Station")
        address = station.get("address", {})
        operator = station.get("operator", {}).get("name", "Unknown")
        num_points = station.get("num_points", 0)
        total_power = station.get("total_power_kw", 0)
        status = station.get("status", {}).get("title", "Unknown")
        
        # Connection details
        connections_html = ""
        for conn in station.get("connections", [])[:3]:
            conn_type = conn.get("type", "Unknown")
            power = conn.get("power_kw", 0)
            qty = conn.get("quantity", 1)
            connections_html += f"<li>{conn_type}: {power}kW x{qty}</li>"
        
        html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; color: #1e40af;">{name}</h4>
            <p style="margin: 4px 0; font-size: 12px; color: #6b7280;">
                {address.get('line1', '')}<br>
                {address.get('city', '')}, {address.get('state', '')} {address.get('postcode', '')}
            </p>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #e5e7eb;">
            <table style="font-size: 12px; width: 100%;">
                <tr><td><b>Operator:</b></td><td>{operator}</td></tr>
                <tr><td><b>Connectors:</b></td><td>{num_points}</td></tr>
                <tr><td><b>Total Power:</b></td><td>{total_power} kW</td></tr>
                <tr><td><b>Status:</b></td><td>{status}</td></tr>
            </table>
            {f'<hr style="margin: 8px 0;"><b>Connections:</b><ul style="margin: 4px 0; padding-left: 20px; font-size: 11px;">{connections_html}</ul>' if connections_html else ''}
        </div>
        """
        return html
    
    def _get_station_icon(self, station: Dict) -> folium.Icon:
        """Get appropriate icon for station based on type."""
        # Determine icon color based on charging level
        has_fast = any(
            c.get("power_kw", 0) > 50 
            for c in station.get("connections", [])
        )
        
        if has_fast:
            color = "green"
            icon = "bolt"
        else:
            color = "blue"
            icon = "plug"
        
        return folium.Icon(color=color, icon=icon, prefix="fa")
    
    def _get_operator_color(self, operator_name: str) -> str:
        """Get color for operator."""
        # Check for partial matches
        for key, color in self.operator_colors.items():
            if key.lower() in operator_name.lower():
                return color
        return self.operator_colors["default"]
    
    # =========================================================================
    # SAVE METHODS
    # =========================================================================
    
    def save_map(self, map_obj: folium.Map, filepath: str) -> str:
        """
        Save map to HTML file.
        
        Args:
            map_obj: Folium map object
            filepath: Output file path
            
        Returns:
            Saved file path
        """
        map_obj.save(filepath)
        return filepath


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🗺️ Map Visualizer")
    print("=" * 60)
    
    # Initialize visualizer
    visualizer = MapVisualizer()
    print("✅ Visualizer initialized")
    
    # Get some test data
    print("\n📍 Fetching test station data...")
    from src.data_access.openchargemap import OpenChargeMapClient
    
    ocm_client = OpenChargeMapClient()
    stations = ocm_client.get_parsed_stations(
        latitude=37.7749,
        longitude=-122.4194,
        radius_km=5,
        max_results=50
    )
    
    print(f"✅ Retrieved {len(stations)} stations")
    
    # Create different map types
    print("\n🗺️ Creating maps...")
    
    # 1. Basic station map
    station_map = visualizer.create_station_map(stations)
    visualizer.save_map(station_map, "data/station_map.html")
    print("   ✅ Station map saved: data/station_map.html")
    
    # 2. Cluster map
    cluster_map = visualizer.create_cluster_map(stations)
    visualizer.save_map(cluster_map, "data/cluster_map.html")
    print("   ✅ Cluster map saved: data/cluster_map.html")
    
    # 3. Heatmap
    heat_map = visualizer.create_heatmap(stations)
    visualizer.save_map(heat_map, "data/heatmap.html")
    print("   ✅ Heatmap saved: data/heatmap.html")
    
    # 4. Operator map
    operator_map = visualizer.create_operator_map(stations)
    visualizer.save_map(operator_map, "data/operator_map.html")
    print("   ✅ Operator map saved: data/operator_map.html")
    
    # 5. Coverage map
    coverage_map = visualizer.create_coverage_map(stations, coverage_radius_km=1)
    visualizer.save_map(coverage_map, "data/coverage_map.html")
    print("   ✅ Coverage map saved: data/coverage_map.html")
    
    print("\n✅ All maps created successfully!")
    print("   Open the HTML files in your browser to view them.")