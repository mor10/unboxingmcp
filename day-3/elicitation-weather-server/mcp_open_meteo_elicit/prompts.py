"""
MCP prompts for weather data assistance and guidance.

This module contains prompt templates that help LLMs interact with the weather
server effectively, providing structured guidance for weather-related queries
and analysis.
"""

from typing import List
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base


def register_prompts(mcp: FastMCP):
    """Register all weather prompts with the MCP server"""
    
    @mcp.prompt(title="Weather Analysis")
    def weather_analysis(location: str, context: str = "") -> str:
        """
        Guide the LLM to perform comprehensive weather analysis for a location.
        
        Args:
            location: Name of the location to analyze weather for
            context: Additional context about what kind of analysis is needed
        """
        base_prompt = f"""Please provide a comprehensive weather analysis for {location}.

Include the following in your analysis:
1. Current weather conditions (temperature, humidity, wind, pressure)
2. Weather forecast for the next 7 days
3. Any weather alerts or severe conditions
4. Recommendations based on the weather conditions
5. Best times for outdoor activities if relevant

Use the available weather tools to gather current data and forecasts."""
        
        if context:
            base_prompt += f"\n\nAdditional context: {context}"
        
        return base_prompt

    @mcp.prompt(title="Travel Weather Advisory")
    def travel_weather_advisory(departure_location: str, destination_location: str, 
                              travel_date: str = "") -> List[base.Message]:
        """
        Create a travel weather advisory comparing conditions between locations.
        
        Args:
            departure_location: Starting location for travel
            destination_location: Destination location
            travel_date: When the travel is planned (optional)
        """
        messages = [
            base.UserMessage(f"I'm planning to travel from {departure_location} to {destination_location}."),
        ]
        
        if travel_date:
            messages.append(base.UserMessage(f"The travel date is: {travel_date}"))
        
        messages.extend([
            base.UserMessage("Can you provide a weather comparison and travel advisory?"),
            base.AssistantMessage("I'll help you with a comprehensive travel weather advisory. Let me check the current conditions and forecasts for both locations."),
            base.AssistantMessage("I'll analyze:"),
            base.AssistantMessage("• Current weather at departure and destination"),
            base.AssistantMessage("• Weather forecasts for your travel period"),
            base.AssistantMessage("• Any weather alerts or warnings"),
            base.AssistantMessage("• Packing recommendations based on conditions"),
            base.AssistantMessage("• Best travel timing if weather conditions vary")
        ])
        
        return messages

    @mcp.prompt(title="Severe Weather Monitor")
    def severe_weather_monitor(location: str) -> str:
        """
        Guide monitoring of severe weather conditions and safety recommendations.
        
        Args:
            location: Location to monitor for severe weather
        """
        return f"""Please monitor severe weather conditions for {location} and provide safety guidance.

Your analysis should include:
1. Check current weather alerts and warnings
2. Identify any immediate severe weather threats (storms, high winds, extreme temperatures)
3. Provide safety recommendations based on current conditions
4. Monitor upcoming weather in the next 24-48 hours for potential threats
5. Suggest preparedness actions if severe weather is expected

Use the weather alert tools to get real-time information and provide actionable advice for staying safe."""

    @mcp.prompt(title="Outdoor Activity Planner")
    def outdoor_activity_planner(location: str, activity: str, 
                               timeframe: str = "next 7 days") -> List[base.Message]:
        """
        Help plan outdoor activities based on weather conditions.
        
        Args:
            location: Location where the activity will take place
            activity: Type of outdoor activity planned
            timeframe: Time period for planning (default: next 7 days)
        """
        return [
            base.UserMessage(f"I want to plan {activity} in {location} for the {timeframe}."),
            base.UserMessage("What are the best weather conditions for this activity?"),
            base.AssistantMessage(f"I'll help you find the best weather windows for {activity} in {location}!"),
            base.AssistantMessage("Let me analyze the weather forecast and identify optimal conditions:"),
            base.AssistantMessage("• Temperature ranges suitable for the activity"),
            base.AssistantMessage("• Precipitation probability and timing"),
            base.AssistantMessage("• Wind conditions and their impact"),
            base.AssistantMessage("• UV index and sun exposure considerations"),
            base.AssistantMessage("• Best time slots within your timeframe"),
            base.AssistantMessage("I'll also suggest backup plans if weather becomes unfavorable.")
        ]

    @mcp.prompt(title="Weather Comparison")
    def weather_comparison(locations: str) -> str:
        """
        Compare weather conditions across multiple locations.
        
        Args:
            locations: Comma-separated list of locations to compare
        """
        location_list = [loc.strip() for loc in locations.split(",")]
        location_names = " vs ".join(location_list)
        
        return f"""Please compare weather conditions across these locations: {location_names}

For each location, gather:
1. Current weather conditions
2. 7-day weather forecast
3. Any active weather alerts

Then provide a comparative analysis including:
• Temperature differences between locations
• Precipitation patterns and likelihood
• Wind and weather severity comparisons  
• Recommendations for which location has the most favorable conditions
• Best and worst weather expected for each location

Present the comparison in an easy-to-read format that highlights key differences."""

    @mcp.prompt(title="Seasonal Weather Insights")
    def seasonal_weather_insights(location: str, season: str = "") -> str:
        """
        Provide insights about seasonal weather patterns and expectations.
        
        Args:
            location: Location to analyze seasonal patterns for
            season: Specific season to focus on (optional)
        """
        base_prompt = f"""Please provide seasonal weather insights for {location}.

Based on current conditions and forecast data:
1. How do current conditions compare to typical seasonal patterns?
2. What weather trends can be expected in the coming weeks?
3. Are there any unusual or noteworthy weather patterns?
4. What should residents and visitors expect for seasonal activities?
5. Any seasonal weather preparedness recommendations?

Use current weather data and forecasts to ground your seasonal analysis."""
        
        if season:
            base_prompt += f"\n\nSpecific focus: Analyze conditions for {season} season."
        
        return base_prompt

    @mcp.prompt(title="Weather Data Interpreter")
    def weather_data_interpreter(weather_data: str) -> List[base.Message]:
        """
        Help interpret and explain weather data in accessible terms.
        
        Args:
            weather_data: Raw or technical weather data to interpret
        """
        return [
            base.UserMessage("I have some weather data that I'd like help understanding:"),
            base.UserMessage(weather_data),
            base.UserMessage("Can you explain what this means in simple terms?"),
            base.AssistantMessage("I'll help you understand this weather information!"),
            base.AssistantMessage("Let me break down the key elements:"),
            base.AssistantMessage("• What the numbers and measurements mean"),
            base.AssistantMessage("• How these conditions will feel and what to expect"),
            base.AssistantMessage("• Any significant weather patterns or changes"),
            base.AssistantMessage("• Practical implications for daily activities"),
            base.AssistantMessage("• Whether any values indicate unusual or noteworthy conditions")
        ]
