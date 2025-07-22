"""
MCP prompts for weather data interactions.

This module contains reusable prompt templates that help LLMs interact 
effectively with the Open-Meteo Weather MCP server, providing guidance 
for weather analysis, forecasting, and interpretation.
"""

from typing import List
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base


def register_prompts(mcp: FastMCP):
    """Register all weather prompts with the MCP server"""

    @mcp.prompt(title="Weather Analysis Assistant")
    def weather_analysis_prompt(location_coordinates: str, context: str = "") -> str:
        """
        Analyze weather conditions and provide insights.
        
        Args:
            location_coordinates: Latitude and longitude (e.g., "40.7128,-74.0060")
            context: Additional context for the analysis
        """
        return f"""You are a weather analysis assistant. I need help analyzing weather conditions for the coordinates {location_coordinates}.

{context if context else ""}

Please help me:
1. Get current weather conditions using the coordinates
2. Analyze the weather patterns and conditions
3. Provide insights about what the weather data means
4. Suggest any relevant observations about the conditions

Use the available weather tools to gather current conditions and forecast data for these coordinates."""

    @mcp.prompt(title="Weather Forecast Planning")
    def forecast_planning_prompt(location_coordinates: str, activity: str, days: int = 7) -> List[base.Message]:
        """
        Plan activities based on weather forecasts.
        
        Args:
            location_coordinates: Latitude and longitude (e.g., "40.7128,-74.0060")
            activity: The activity to plan for
            days: Number of days to forecast (default 7)
        """
        return [
            base.UserMessage(f"I'm planning to {activity} at coordinates {location_coordinates} in the next {days} days."),
            base.UserMessage("Can you help me plan by analyzing the weather forecast?"),
            base.AssistantMessage(f"I'll help you plan your {activity} by analyzing the weather forecast. Let me get the {days}-day forecast for coordinates {location_coordinates} and provide recommendations based on the conditions."),
            base.UserMessage("Please use the weather forecast tools to get the data and then provide specific recommendations for the best days and times.")
        ]

    @mcp.prompt(title="Weather Data Interpretation")
    def weather_interpretation_prompt(weather_data: str) -> str:
        """
        Help interpret weather data and codes.
        
        Args:
            weather_data: Raw weather data or specific values to interpret
        """
        return f"""Please help me interpret this weather data:

{weather_data}

I need help understanding:
- What the weather codes mean in plain language
- Whether these conditions are typical or unusual
- What practical implications these conditions have
- Any safety considerations or recommendations

Please explain the data in clear, easy-to-understand terms."""

    @mcp.prompt(title="Coordinate Weather Resources")
    def weather_resources_guide(latitude: str, longitude: str) -> List[base.Message]:
        """
        Guide for accessing weather resources using coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        """
        return [
            base.UserMessage(f"I want to access weather information for coordinates {latitude}, {longitude}."),
            base.AssistantMessage("I can help you access weather data for those coordinates. The server provides several ways to get weather information:"),
            base.AssistantMessage(f"1. Current weather resource: weather://current/{latitude},{longitude}"),
            base.AssistantMessage(f"2. Weather forecast resource: weather://forecast/{latitude},{longitude}"),
            base.AssistantMessage("3. Tools for detailed current weather and custom forecasts"),
            base.UserMessage("Which type of weather information would you like me to retrieve?")
        ]

    @mcp.prompt(title="Weather Comparison Analysis")
    def weather_comparison_prompt(location1_coords: str, location2_coords: str) -> str:
        """
        Compare weather conditions between two locations.
        
        Args:
            location1_coords: First location coordinates (e.g., "40.7128,-74.0060")
            location2_coords: Second location coordinates (e.g., "34.0522,-118.2437")
        """
        return f"""I want to compare the weather conditions between two locations:

Location 1: {location1_coords}
Location 2: {location2_coords}

Please help me:
1. Get current weather data for both locations
2. Get forecasts for both locations
3. Compare the conditions side by side
4. Highlight significant differences
5. Provide insights about which location has more favorable conditions

Use the weather tools to gather data for both coordinate pairs and present a comprehensive comparison."""

    @mcp.prompt(title="Weather Alert Assessment")
    def weather_alert_prompt(location_coordinates: str, activity_type: str = "general") -> List[base.Message]:
        """
        Assess weather conditions for potential safety concerns.
        
        Args:
            location_coordinates: Latitude and longitude coordinates
            activity_type: Type of activity (outdoor, travel, sports, etc.)
        """
        return [
            base.UserMessage(f"I need to assess weather conditions at {location_coordinates} for {activity_type} activities."),
            base.UserMessage("Can you check for any concerning weather conditions?"),
            base.AssistantMessage(f"I'll analyze the current weather and forecast for {location_coordinates} to identify any conditions that might affect {activity_type} activities."),
            base.UserMessage("Please look for:"),
            base.UserMessage("- High winds, storms, or severe weather"),
            base.UserMessage("- Temperature extremes"),
            base.UserMessage("- Precipitation that might cause issues"),
            base.UserMessage("- Any other safety considerations"),
            base.AssistantMessage("Let me get the current conditions and forecast to provide a comprehensive safety assessment.")
        ]

    @mcp.prompt(title="Travel Weather Planning")
    def travel_weather_prompt(departure_coords: str, destination_coords: str, travel_date: str = "today") -> str:
        """
        Plan travel based on weather at departure and destination locations.
        
        Args:
            departure_coords: Starting location coordinates
            destination_coords: Destination coordinates  
            travel_date: Date of travel (default "today")
        """
        return f"""I'm planning travel from {departure_coords} to {destination_coords} on {travel_date}.

Please help me with weather-based travel planning:

1. Current conditions at departure location ({departure_coords})
2. Current conditions at destination ({destination_coords})  
3. Weather forecast for both locations
4. Travel recommendations based on weather patterns
5. What to pack or prepare for based on weather differences
6. Best timing for departure if weather is a factor

Use the weather tools to gather comprehensive data for both coordinate pairs and provide travel-specific advice."""
