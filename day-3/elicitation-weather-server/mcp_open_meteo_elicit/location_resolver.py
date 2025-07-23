"""
Location resolution and disambiguation logic.

This module handles resolving location names to coordinates, including
managing ambiguous location results through MCP elicitation when multiple
locations are found for a given search term.

MCP specification: https://modelcontextprotocol.io/specification/draft/client/elicitation
SDK documentation: https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#elicitation
"""

from mcp.server.fastmcp import Context # 
from .models import LocationInfo, LocationChoice
from .api_client import search_locations
from .config import MAX_LOCATION_ELICITATION_OPTIONS


async def resolve_location(location_name: str, ctx: Context) -> LocationInfo:
    """
    Resolve a location name to coordinates, handling ambiguous results with elicitation
    """
    locations = await search_locations(location_name, limit=10)
    
    if not locations:
        raise ValueError(f"No locations found for '{location_name}'. Please try a different search term.")
    
    if len(locations) == 1:
        # Single result, use it directly
        loc = locations[0]
        return LocationInfo(
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
        )
    
    # Multiple results - use elicitation to let user choose
    location_options = []
    for i, loc in enumerate(locations[:MAX_LOCATION_ELICITATION_OPTIONS]):  # Limit to top 5 for usability
        admin_parts = []
        if loc.get("admin1"):
            admin_parts.append(loc["admin1"])
        if loc.get("admin2") and loc.get("admin2") != loc.get("admin1"):
            admin_parts.append(loc["admin2"])
        
        admin_str = f", {', '.join(admin_parts)}" if admin_parts else ""
        pop_str = f" (pop. {loc['population']:,})" if loc.get("population") else ""
        
        location_options.append(
            f"{i+1}. {loc['name']}{admin_str}, {loc['country']}{pop_str}"
        )
    
    options_text = "\n".join(location_options)
    
    # Create elicitation message
    message = f"Multiple locations found for '{location_name}':\n\n{options_text}\n\nPlease select the correct location:"
    
    # Use elicitation to get user choice
    # @link https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#elicitation
    result = await ctx.elicit(
        message=message,
        schema=LocationChoice
    )
    
    if result.action != "accept" or not result.data:
        raise ValueError("Location selection was cancelled or invalid.")
    
    selected_index = result.data.selected_location_id - 1
    if selected_index < 0 or selected_index >= len(locations[:MAX_LOCATION_ELICITATION_OPTIONS]):
        raise ValueError("Invalid location selection. Please choose a number from the list.")
    
    selected_location = locations[selected_index]
    return LocationInfo(
        id=selected_location["id"],
        name=selected_location["name"],
        latitude=selected_location["latitude"],
        longitude=selected_location["longitude"],
        country=selected_location.get("country", ""),
        admin1=selected_location.get("admin1"),
        admin2=selected_location.get("admin2"),
        timezone=selected_location["timezone"],
        population=selected_location.get("population"),
        elevation=selected_location.get("elevation")
    )
