"""
Configuration settings for the Open-Meteo Weather MCP Server.

This module contains API endpoints, default parameters, and other
configuration constants used throughout the application.
"""

# API Endpoints
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Default Parameters
DEFAULT_TEMPERATURE_UNIT = "celsius"
DEFAULT_WIND_SPEED_UNIT = "kmh"
DEFAULT_PRECIPITATION_UNIT = "mm"
DEFAULT_FORECAST_DAYS = 7
DEFAULT_FORECAST_HOURS = 24
MAX_FORECAST_DAYS = 16
MAX_FORECAST_HOURS = 168
MAX_LOCATION_SEARCH_RESULTS = 100

# Weather Alert Thresholds
HIGH_WIND_THRESHOLD_KMH = 50  # km/h
SEVERE_WEATHER_CODES = [95, 96, 99]  # Thunderstorms
FREEZING_RAIN_CODES = [66, 67]
SNOW_CODES = [71, 73, 75]
