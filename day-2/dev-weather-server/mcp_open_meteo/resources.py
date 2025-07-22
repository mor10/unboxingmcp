"""
MCP resources for weather data access.

This module contains resource handlers that provide weather information
in a read-only format, accessible via URI-based resource requests using coordinates.
"""

from mcp.server.fastmcp import FastMCP
from .api_client import get_weather_data
from .constants import weather_code_to_description


def register_resources(mcp: FastMCP):
    """Register all weather resources with the MCP server"""
    
    @mcp.resource("weather://current/{latitude},{longitude}")
    async def current_weather_resource(latitude: str, longitude: str) -> str:
        """Get current weather as a resource"""
        try:
            lat = float(latitude)
            lng = float(longitude)
        except ValueError:
            return f"Invalid coordinates: {latitude},{longitude}"
        
        current_params = [
            "temperature_2m", "relative_humidity_2m", "weather_code",
            "wind_speed_10m", "wind_direction_10m", "pressure_msl", "cloud_cover"
        ]
        
        weather_data = await get_weather_data(
            lat, lng,
            current=current_params
        )
        
        current = weather_data["current"]
        weather_desc = weather_code_to_description(current["weather_code"])
        
        return f"""Current Weather for {lat}, {lng}
Temperature: {current['temperature_2m']}°C
Weather: {weather_desc}
Humidity: {current['relative_humidity_2m']}%
Wind: {current['wind_speed_10m']} km/h from {current['wind_direction_10m']}°
Pressure: {current['pressure_msl']} hPa
Cloud Cover: {current['cloud_cover']}%
Last Updated: {current['time']}"""

    @mcp.resource("weather://forecast/{latitude},{longitude}")
    async def forecast_resource(latitude: str, longitude: str) -> str:
        """Get weather forecast as a resource"""
        try:
            lat = float(latitude)
            lng = float(longitude)
        except ValueError:
            return f"Invalid coordinates: {latitude},{longitude}"
        
        daily_params = [
            "temperature_2m_max", "temperature_2m_min", "weather_code", "precipitation_sum"
        ]
        
        weather_data = await get_weather_data(
            lat, lng,
            daily=daily_params,
            forecast_days=7
        )
        
        daily = weather_data["daily"]
        
        # Build forecast entries
        forecast_entries = []
        for i in range(len(daily["time"])):
            date = daily["time"][i]
            max_temp = daily["temperature_2m_max"][i]
            min_temp = daily["temperature_2m_min"][i]
            weather_desc = weather_code_to_description(daily["weather_code"][i])
            precip = daily["precipitation_sum"][i]
            
            forecast_entries.append(f"{date}: {weather_desc}\n  High: {max_temp}°C, Low: {min_temp}°C\n  Precipitation: {precip}mm")
        
        return f"""7-Day Weather Forecast for {lat}, {lng}

{chr(10).join(forecast_entries)}"""
