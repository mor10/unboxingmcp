"""
Location resolution and disambiguation logic.

This module handles resolving location names to coordinates.
When multiple locations are found, it returns the first (most relevant) location.
"""

from .models import LocationInfo
from .api_client import search_locations


async def resolve_location(location_name: str) -> LocationInfo:
    """
    Resolve a location name to coordinates, returning the first location when multiple are found
    """
    locations = await search_locations(location_name, limit=10)
    
    if not locations:
        raise ValueError(f"No locations found for '{location_name}'. Please try a different search term.")
    
    # Always use the first result (most relevant according to the API)
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
