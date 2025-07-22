"""
MCP tools for weather data retrieval and location services.

This module contains all the tool functions that are exposed via the MCP server,
including weather forecasting, current conditions, and location search capabilities.
"""

from typing import List, Dict, Any
from datetime import datetime
from mcp.server.fastmcp import FastMCP

from .models import (
    LocationInfo, CurrentWeather, WeatherForecast, DailyForecast,
    HourlyForecast, HourlyWeatherPoint
)
from .api_client import search_locations, get_weather_data
from .location_resolver import resolve_location
from .constants import weather_code_to_description
from .config import (
    MAX_FORECAST_DAYS, MAX_FORECAST_HOURS, HIGH_WIND_THRESHOLD_KMH,
    SEVERE_WEATHER_CODES, FREEZING_RAIN_CODES, SNOW_CODES
)


def register_tools(mcp: FastMCP):
    """Register all weather tools with the MCP server"""
    
    @mcp.tool()
    async def search_locations_tool(location_name: str, limit: int = 5) -> List[LocationInfo]:
        """
        Search for locations by name or postal code.
        
        Args:
            location_name: Name of city, region, or postal code to search for
            limit: Maximum number of results to return (1-10, default 5)
        """
        if len(location_name.strip()) < 2:
            raise ValueError("Location name must be at least 2 characters long.")
        
        limit = max(1, min(limit, 10))  # Clamp between 1 and 10
        locations = await search_locations(location_name, limit)
        
        result = []
        for loc in locations:
            result.append(LocationInfo(
                id=loc["id"],
                name=loc["name"],
                latitude=loc["latitude"],
                longitude=loc["longitude"],
                country=loc.get("country", ""),
                admin1=loc.get("admin1"),
                admin2=loc.get("admin2"),
                timezone=loc["timezone"],
                population=loc.get("population"),
                elevation=loc.get("elevation")
            ))
        
        return result

    @mcp.tool()
    async def get_current_weather(location_name: str, 
                                temperature_unit: str = "celsius") -> CurrentWeather:
        """
        Get current weather conditions for a location.
        
        Args:
            location_name: Name of the location (city, region, etc.)
            temperature_unit: Temperature unit ("celsius" or "fahrenheit")
        """
        location = await resolve_location(location_name)
        
        current_params = [
            "temperature_2m", "relative_humidity_2m", "weather_code",
            "wind_speed_10m", "wind_direction_10m", "pressure_msl", "cloud_cover"
        ]
        
        weather_data = await get_weather_data(
            location.latitude, location.longitude,
            current=current_params,
            temperature_unit=temperature_unit
        )
        
        current = weather_data["current"]
        
        return CurrentWeather(
            location=location,
            temperature=current["temperature_2m"],
            temperature_unit=weather_data["current_units"]["temperature_2m"],
            humidity=current["relative_humidity_2m"],
            weather_description=weather_code_to_description(current["weather_code"]),
            weather_code=current["weather_code"],
            wind_speed=current["wind_speed_10m"],
            wind_direction=current["wind_direction_10m"],
            wind_speed_unit=weather_data["current_units"]["wind_speed_10m"],
            pressure=current["pressure_msl"],
            cloud_cover=current["cloud_cover"],
            timestamp=current["time"]
        )

    @mcp.tool()
    async def get_weather_forecast(location_name: str,
                                 forecast_days: int = 7,
                                 temperature_unit: str = "celsius") -> WeatherForecast:
        """
        Get daily weather forecast for a location.
        
        Args:
            location_name: Name of the location (city, region, etc.)
            forecast_days: Number of forecast days (1-16, default 7)
            temperature_unit: Temperature unit ("celsius" or "fahrenheit")
        """
        location = await resolve_location(location_name)
        forecast_days = max(1, min(forecast_days, MAX_FORECAST_DAYS))
        
        daily_params = [
            "temperature_2m_max", "temperature_2m_min", "weather_code",
            "precipitation_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"
        ]
        
        weather_data = await get_weather_data(
            location.latitude, location.longitude,
            daily=daily_params,
            forecast_days=forecast_days,
            temperature_unit=temperature_unit
        )
        
        daily = weather_data["daily"]
        daily_units = weather_data["daily_units"]
        
        forecast_days_list = []
        for i in range(len(daily["time"])):
            forecast_days_list.append(DailyForecast(
                date=daily["time"][i],
                temperature_max=daily["temperature_2m_max"][i],
                temperature_min=daily["temperature_2m_min"][i],
                temperature_unit=daily_units["temperature_2m_max"],
                weather_description=weather_code_to_description(daily["weather_code"][i]),
                weather_code=daily["weather_code"][i],
                precipitation_sum=daily["precipitation_sum"][i],
                precipitation_unit=daily_units["precipitation_sum"],
                wind_speed_max=daily["wind_speed_10m_max"][i],
                wind_direction_dominant=daily["wind_direction_10m_dominant"][i],
                wind_speed_unit=daily_units["wind_speed_10m_max"]
            ))
        
        return WeatherForecast(
            location=location,
            forecast_days=forecast_days_list,
            generated_at=datetime.now().isoformat()
        )

    @mcp.tool()
    async def get_hourly_forecast(location_name: str,
                                forecast_hours: int = 24,
                                temperature_unit: str = "celsius") -> HourlyForecast:
        """
        Get hourly weather forecast for a location.
        
        Args:
            location_name: Name of the location (city, region, etc.)
            forecast_hours: Number of forecast hours (1-168, default 24)
            temperature_unit: Temperature unit ("celsius" or "fahrenheit")
        """
        location = await resolve_location(location_name)
        forecast_hours = max(1, min(forecast_hours, MAX_FORECAST_HOURS))
        
        hourly_params = [
            "temperature_2m", "relative_humidity_2m", "weather_code",
            "precipitation", "wind_speed_10m", "wind_direction_10m", "cloud_cover"
        ]
        
        weather_data = await get_weather_data(
            location.latitude, location.longitude,
            hourly=hourly_params,
            temperature_unit=temperature_unit
        )
        
        hourly = weather_data["hourly"]
        hourly_units = weather_data["hourly_units"]
        
        # Limit to requested hours
        hourly_data = []
        for i in range(min(forecast_hours, len(hourly["time"]))):
            hourly_data.append(HourlyWeatherPoint(
                time=hourly["time"][i],
                temperature=hourly["temperature_2m"][i],
                humidity=hourly["relative_humidity_2m"][i],
                weather_code=hourly["weather_code"][i],
                weather_description=weather_code_to_description(hourly["weather_code"][i]),
                precipitation=hourly["precipitation"][i],
                wind_speed=hourly["wind_speed_10m"][i],
                wind_direction=hourly["wind_direction_10m"][i],
                cloud_cover=hourly["cloud_cover"][i]
            ))
        
        return HourlyForecast(
            location=location,
            hourly_data=hourly_data,
            temperature_unit=hourly_units["temperature_2m"],
            precipitation_unit=hourly_units["precipitation"],
            wind_speed_unit=hourly_units["wind_speed_10m"],
            generated_at=datetime.now().isoformat()
        )

    @mcp.tool()
    async def get_weather_alerts(location_name: str) -> Dict[str, Any]:
        """
        Check for severe weather conditions and alerts for a location.
        
        Args:
            location_name: Name of the location (city, region, etc.)
        """
        location = await resolve_location(location_name)
        
        # Get current and near-term forecast for alert analysis
        current_params = ["temperature_2m", "weather_code", "wind_speed_10m", "precipitation"]
        hourly_params = ["temperature_2m", "weather_code", "wind_speed_10m", "precipitation", "wind_gusts_10m"]
        
        weather_data = await get_weather_data(
            location.latitude, location.longitude,
            current=current_params,
            hourly=hourly_params,
            forecast_days=2  # Check next 48 hours
        )
        
        alerts = []
        current = weather_data["current"]
        hourly = weather_data["hourly"]
        
        # Check for severe weather conditions
        current_weather_code = current["weather_code"]
        if current_weather_code in SEVERE_WEATHER_CODES:  # Thunderstorms
            alerts.append({
                "type": "severe_weather",
                "severity": "high",
                "title": "Thunderstorm Warning",
                "description": weather_code_to_description(current_weather_code),
                "time": "current"
            })
        elif current_weather_code in FREEZING_RAIN_CODES:  # Freezing rain
            alerts.append({
                "type": "severe_weather", 
                "severity": "high",
                "title": "Freezing Rain Warning",
                "description": weather_code_to_description(current_weather_code),
                "time": "current"
            })
        elif current_weather_code in SNOW_CODES:  # Snow
            alerts.append({
                "type": "weather_advisory",
                "severity": "medium",
                "title": "Snow Advisory",
                "description": weather_code_to_description(current_weather_code),
                "time": "current"
            })
        
        # Check wind conditions
        current_wind = current["wind_speed_10m"]
        if current_wind > HIGH_WIND_THRESHOLD_KMH:  # > 50 km/h
            alerts.append({
                "type": "wind_warning",
                "severity": "medium",
                "title": "High Wind Warning",
                "description": f"Strong winds at {current_wind} km/h",
                "time": "current"
            })
        
        # Check for upcoming severe weather in next 24 hours
        for i in range(min(24, len(hourly["time"]))):
            weather_code = hourly["weather_code"][i]
            if weather_code in SEVERE_WEATHER_CODES and not any(alert["type"] == "severe_weather" for alert in alerts):
                alerts.append({
                    "type": "severe_weather",
                    "severity": "medium",
                    "title": "Incoming Thunderstorm",
                    "description": f"Thunderstorm expected at {hourly['time'][i]}",
                    "time": hourly["time"][i]
                })
                break
        
        return {
            "location": location,
            "alerts": alerts,
            "alert_count": len(alerts),
            "checked_at": datetime.now().isoformat()
        }
