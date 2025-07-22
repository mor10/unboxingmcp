"""
MCP tools for weather data retrieval.

This module contains all the tool functions that are exposed via the MCP server,
including weather forecasting and current conditions using latitude and longitude coordinates.
"""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

from .models import (
    CurrentWeather, WeatherForecast, DailyForecast
)
from .api_client import get_weather_data
from .constants import weather_code_to_description
from .config import (
    MAX_FORECAST_DAYS
)


def register_tools(mcp: FastMCP):
    """Register all weather tools with the MCP server"""
    
    @mcp.tool()
    async def get_current_weather(latitude: float, longitude: float, 
                                temperature_unit: str = "celsius") -> CurrentWeather:
        """
        Get current weather conditions for a location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            temperature_unit: Temperature unit ("celsius" or "fahrenheit")
        """
        current_params = [
            "temperature_2m", "relative_humidity_2m", "weather_code",
            "wind_speed_10m", "wind_direction_10m", "pressure_msl", "cloud_cover"
        ]
        
        weather_data = await get_weather_data(
            latitude, longitude,
            current=current_params,
            temperature_unit=temperature_unit
        )
        
        current = weather_data["current"]
        
        return CurrentWeather(
            latitude=latitude,
            longitude=longitude,
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
    async def get_weather_forecast(latitude: float, longitude: float,
                                 forecast_days: int = 7,
                                 temperature_unit: str = "celsius") -> WeatherForecast:
        """
        Get daily weather forecast for a location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            forecast_days: Number of forecast days (1-16, default 7)
            temperature_unit: Temperature unit ("celsius" or "fahrenheit")
        """
        forecast_days = max(1, min(forecast_days, MAX_FORECAST_DAYS))
        
        daily_params = [
            "temperature_2m_max", "temperature_2m_min", "weather_code",
            "precipitation_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"
        ]
        
        weather_data = await get_weather_data(
            latitude, longitude,
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
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days_list,
            generated_at=datetime.now().isoformat()
        )

   