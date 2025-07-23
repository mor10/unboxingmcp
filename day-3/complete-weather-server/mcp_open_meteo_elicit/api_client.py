"""
API client for interacting with Open-Meteo services.

This module handles all HTTP communication with the Open-Meteo geocoding
and weather forecast APIs, including error handling and response parsing.
"""

import httpx
from typing import List, Dict, Any, Optional
from .config import GEOCODING_API_URL, WEATHER_API_URL, MAX_LOCATION_SEARCH_RESULTS


async def search_locations(location_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for locations using the geocoding API"""
    params = {
        "name": location_name,
        "count": min(limit, MAX_LOCATION_SEARCH_RESULTS),
        "format": "json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(GEOCODING_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            error_data = response.json()
            raise ValueError(f"Geocoding API error: {error_data.get('reason', 'Unknown error')}")


async def get_weather_data(latitude: float, longitude: float, 
                          current: Optional[List[str]] = None,
                          hourly: Optional[List[str]] = None,
                          daily: Optional[List[str]] = None,
                          forecast_days: int = 7,
                          temperature_unit: str = "celsius",
                          wind_speed_unit: str = "kmh",
                          precipitation_unit: str = "mm") -> Dict[str, Any]:
    """Get weather data from Open-Meteo forecast API"""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": temperature_unit,
        "wind_speed_unit": wind_speed_unit,
        "precipitation_unit": precipitation_unit,
        "forecast_days": forecast_days
    }
    
    if current:
        params["current"] = ",".join(current)
    if hourly:
        params["hourly"] = ",".join(hourly)
    if daily:
        params["daily"] = ",".join(daily)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(WEATHER_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise ValueError(f"Weather API error: {error_data.get('reason', 'Unknown error')}")
