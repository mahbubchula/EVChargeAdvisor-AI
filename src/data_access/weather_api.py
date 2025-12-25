"""
🌤️ Open-Meteo Weather API Client
=================================

Fetches weather and climate data for EV range impact analysis.

Author: MAHBUB
Date: December 25, 2024
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.data_access.base_api import BaseAPIClient, APIError
from config.api_keys import API_CONFIGS
from config.settings import WEATHER_SETTINGS


class WeatherAPIClient(BaseAPIClient):
    """
    Client for Open-Meteo Weather API.
    
    Open-Meteo provides free weather data without API key.
    Perfect for analyzing climate impact on EV charging.
    """
    
    # Weather codes interpretation
    WEATHER_CODES = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    
    # EV range impact by temperature (approximate % of normal range)
    EV_RANGE_IMPACT = {
        -20: 0.50,  # 50% range at -20°C
        -10: 0.60,  # 60% range at -10°C
        0: 0.75,    # 75% range at 0°C
        10: 0.90,   # 90% range at 10°C
        20: 1.00,   # 100% range at 20°C (optimal)
        25: 1.00,   # 100% range at 25°C
        30: 0.95,   # 95% range at 30°C
        35: 0.90,   # 90% range at 35°C
        40: 0.85,   # 85% range at 40°C
    }
    
    def __init__(self):
        """Initialize Weather API client."""
        config = API_CONFIGS["openmeteo"]
        super().__init__(
            base_url=config["base_url"],
            api_key=config.get("api_key")  # No API key needed
        )
        self.settings = WEATHER_SETTINGS
    
    def _add_auth_params(self, params: Dict) -> Dict:
        """No authentication needed for Open-Meteo."""
        return params
    
    # =========================================================================
    # MAIN METHODS
    # =========================================================================
    
    def get_current_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get current weather for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Current weather dictionary
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation",
            "temperature_unit": self.settings.get("temperature_unit", "celsius"),
            "timezone": "auto"
        }
        
        try:
            response = self.get("forecast", params=params)
            current = response.get("current", {})
            
            weather_code = current.get("weather_code", 0)
            temperature = current.get("temperature_2m", 20)
            
            return {
                "temperature": temperature,
                "temperature_unit": "°C",
                "humidity": current.get("relative_humidity_2m"),
                "precipitation": current.get("precipitation", 0),
                "wind_speed": current.get("wind_speed_10m"),
                "weather_code": weather_code,
                "weather_description": self.WEATHER_CODES.get(weather_code, "Unknown"),
                "ev_range_factor": self._calculate_range_factor(temperature),
                "timestamp": current.get("time"),
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": response.get("timezone")
                }
            }
            
        except Exception as e:
            print(f"❌ Weather API Error: {e}")
            return {}
    
    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of forecast days (1-16)
            
        Returns:
            Forecast dictionary with daily data
        """
        days = min(max(days, 1), 16)  # Clamp between 1 and 16
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,weather_code,wind_speed_10m_max",
            "temperature_unit": self.settings.get("temperature_unit", "celsius"),
            "timezone": "auto",
            "forecast_days": days
        }
        
        try:
            response = self.get("forecast", params=params)
            daily = response.get("daily", {})
            
            # Parse into list of daily forecasts
            forecasts = []
            dates = daily.get("time", [])
            
            for i, date in enumerate(dates):
                temp_mean = daily.get("temperature_2m_mean", [None])[i]
                forecasts.append({
                    "date": date,
                    "temperature_max": daily.get("temperature_2m_max", [None])[i],
                    "temperature_min": daily.get("temperature_2m_min", [None])[i],
                    "temperature_mean": temp_mean,
                    "precipitation": daily.get("precipitation_sum", [0])[i],
                    "weather_code": daily.get("weather_code", [0])[i],
                    "weather_description": self.WEATHER_CODES.get(
                        daily.get("weather_code", [0])[i], "Unknown"
                    ),
                    "wind_speed_max": daily.get("wind_speed_10m_max", [None])[i],
                    "ev_range_factor": self._calculate_range_factor(temp_mean) if temp_mean else 1.0
                })
            
            return {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": response.get("timezone")
                },
                "forecast_days": len(forecasts),
                "daily_forecasts": forecasts,
                "summary": self._summarize_forecast(forecasts)
            }
            
        except Exception as e:
            print(f"❌ Weather API Error: {e}")
            return {}
    
    def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get historical weather data.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Historical weather dictionary
        """
        # Use archive API endpoint
        archive_url = "https://archive-api.open-meteo.com/v1/archive"
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum",
            "temperature_unit": self.settings.get("temperature_unit", "celsius"),
            "timezone": "auto"
        }
        
        try:
            response = self.session.get(archive_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            
            records = []
            for i, date in enumerate(dates):
                records.append({
                    "date": date,
                    "temperature_max": daily.get("temperature_2m_max", [None])[i],
                    "temperature_min": daily.get("temperature_2m_min", [None])[i],
                    "temperature_mean": daily.get("temperature_2m_mean", [None])[i],
                    "precipitation": daily.get("precipitation_sum", [0])[i]
                })
            
            return {
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "period": {
                    "start": start_date,
                    "end": end_date,
                    "days": len(records)
                },
                "records": records,
                "statistics": self._calculate_statistics(records)
            }
            
        except Exception as e:
            print(f"❌ Weather API Error: {e}")
            return {}
    
    # =========================================================================
    # EV RANGE ANALYSIS
    # =========================================================================
    
    def _calculate_range_factor(self, temperature: float) -> float:
        """
        Calculate EV range factor based on temperature.
        
        Args:
            temperature: Temperature in Celsius
            
        Returns:
            Range factor (1.0 = 100% range)
        """
        if temperature is None:
            return 1.0
        
        # Find closest temperature points for interpolation
        temps = sorted(self.EV_RANGE_IMPACT.keys())
        
        if temperature <= temps[0]:
            return self.EV_RANGE_IMPACT[temps[0]]
        if temperature >= temps[-1]:
            return self.EV_RANGE_IMPACT[temps[-1]]
        
        # Linear interpolation
        for i in range(len(temps) - 1):
            if temps[i] <= temperature <= temps[i + 1]:
                t1, t2 = temps[i], temps[i + 1]
                r1, r2 = self.EV_RANGE_IMPACT[t1], self.EV_RANGE_IMPACT[t2]
                factor = r1 + (r2 - r1) * (temperature - t1) / (t2 - t1)
                return round(factor, 2)
        
        return 1.0
    
    def analyze_ev_range_impact(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Analyze EV range impact based on current and forecast weather.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            EV range impact analysis
        """
        current = self.get_current_weather(latitude, longitude)
        forecast = self.get_forecast(latitude, longitude, days=7)
        
        if not current or not forecast:
            return {}
        
        current_temp = current.get("temperature", 20)
        current_factor = current.get("ev_range_factor", 1.0)
        
        # Calculate forecast factors
        forecast_factors = [
            f.get("ev_range_factor", 1.0) 
            for f in forecast.get("daily_forecasts", [])
        ]
        
        avg_factor = sum(forecast_factors) / len(forecast_factors) if forecast_factors else 1.0
        min_factor = min(forecast_factors) if forecast_factors else 1.0
        max_factor = max(forecast_factors) if forecast_factors else 1.0
        
        # Determine impact level
        if current_factor >= 0.95:
            impact_level = "Minimal"
            impact_color = "green"
        elif current_factor >= 0.85:
            impact_level = "Low"
            impact_color = "blue"
        elif current_factor >= 0.70:
            impact_level = "Moderate"
            impact_color = "orange"
        else:
            impact_level = "High"
            impact_color = "red"
        
        return {
            "current": {
                "temperature": current_temp,
                "range_factor": current_factor,
                "range_percentage": f"{int(current_factor * 100)}%",
                "weather": current.get("weather_description")
            },
            "forecast_7day": {
                "avg_range_factor": round(avg_factor, 2),
                "min_range_factor": round(min_factor, 2),
                "max_range_factor": round(max_factor, 2)
            },
            "impact": {
                "level": impact_level,
                "color": impact_color,
                "recommendation": self._get_range_recommendation(current_factor)
            }
        }
    
    def _get_range_recommendation(self, factor: float) -> str:
        """Get recommendation based on range factor."""
        if factor >= 0.95:
            return "Optimal conditions for EV charging and driving."
        elif factor >= 0.85:
            return "Good conditions. Minor range reduction expected."
        elif factor >= 0.70:
            return "Plan for reduced range. Consider charging more frequently."
        else:
            return "Significant range reduction. Plan routes carefully and charge frequently."
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _summarize_forecast(self, forecasts: List[Dict]) -> Dict[str, Any]:
        """Summarize forecast data."""
        if not forecasts:
            return {}
        
        temps = [f.get("temperature_mean") for f in forecasts if f.get("temperature_mean")]
        precip = [f.get("precipitation", 0) for f in forecasts]
        
        return {
            "avg_temperature": round(sum(temps) / len(temps), 1) if temps else None,
            "min_temperature": min([f.get("temperature_min", 100) for f in forecasts]),
            "max_temperature": max([f.get("temperature_max", -100) for f in forecasts]),
            "total_precipitation": round(sum(precip), 1),
            "rainy_days": sum(1 for p in precip if p > 0)
        }
    
    def _calculate_statistics(self, records: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics for historical data."""
        if not records:
            return {}
        
        temps = [r.get("temperature_mean") for r in records if r.get("temperature_mean")]
        precip = [r.get("precipitation", 0) for r in records]
        
        return {
            "avg_temperature": round(sum(temps) / len(temps), 1) if temps else None,
            "min_temperature": min(temps) if temps else None,
            "max_temperature": max(temps) if temps else None,
            "total_precipitation": round(sum(precip), 1),
            "avg_precipitation": round(sum(precip) / len(precip), 2) if precip else 0
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🌤️ Open-Meteo Weather API Client")
    print("=" * 60)
    
    # Initialize client
    client = WeatherAPIClient()
    print(f"✅ Client initialized: {client}")
    
    # Test: Get current weather for San Francisco
    print("\n📍 Fetching current weather for San Francisco...")
    current = client.get_current_weather(
        latitude=37.7749,
        longitude=-122.4194
    )
    
    if current:
        print(f"✅ Current Weather:")
        print(f"   Temperature: {current['temperature']}°C")
        print(f"   Condition: {current['weather_description']}")
        print(f"   Humidity: {current['humidity']}%")
        print(f"   EV Range Factor: {current['ev_range_factor']} ({int(current['ev_range_factor']*100)}%)")
    
    # Test: Get 7-day forecast
    print("\n📍 Fetching 7-day forecast...")
    forecast = client.get_forecast(
        latitude=37.7749,
        longitude=-122.4194,
        days=7
    )
    
    if forecast:
        print(f"✅ Forecast retrieved for {forecast['forecast_days']} days")
        print("\n📋 Daily Forecast:")
        for day in forecast['daily_forecasts'][:3]:
            print(f"   {day['date']}: {day['temperature_min']}°C - {day['temperature_max']}°C, {day['weather_description']}")
        
        summary = forecast['summary']
        print(f"\n📊 Summary:")
        print(f"   Avg Temp: {summary['avg_temperature']}°C")
        print(f"   Rainy Days: {summary['rainy_days']}")
    
    # Test: EV Range Impact Analysis
    print("\n📍 Analyzing EV range impact...")
    impact = client.analyze_ev_range_impact(
        latitude=37.7749,
        longitude=-122.4194
    )
    
    if impact:
        print(f"✅ EV Range Analysis:")
        print(f"   Current Range: {impact['current']['range_percentage']}")
        print(f"   Impact Level: {impact['impact']['level']}")
        print(f"   Recommendation: {impact['impact']['recommendation']}")