"""
Data models for the Open-Meteo Weather MCP Server.

This module contains all Pydantic models used for structured data representation
in the weather API responses.
"""

from typing import List
from pydantic import BaseModel


class CurrentWeather(BaseModel):
    """Current weather conditions"""
    latitude: float
    longitude: float
    temperature: float
    temperature_unit: str
    humidity: int
    weather_description: str
    weather_code: int
    wind_speed: float
    wind_direction: int
    wind_speed_unit: str
    pressure: float
    cloud_cover: int
    timestamp: str


class DailyForecast(BaseModel):
    """Daily weather forecast"""
    date: str
    temperature_max: float
    temperature_min: float
    temperature_unit: str
    weather_description: str
    weather_code: int
    precipitation_sum: float
    precipitation_unit: str
    wind_speed_max: float
    wind_direction_dominant: int
    wind_speed_unit: str


class WeatherForecast(BaseModel):
    """Multi-day weather forecast"""
    latitude: float
    longitude: float
    forecast_days: List[DailyForecast]
    generated_at: str


class HourlyWeatherPoint(BaseModel):
    """Single hourly weather data point"""
    time: str
    temperature: float
    humidity: int
    weather_code: int
    weather_description: str
    precipitation: float
    wind_speed: float
    wind_direction: int
    cloud_cover: int


class HourlyForecast(BaseModel):
    """Hourly weather forecast"""
    latitude: float
    longitude: float
    hourly_data: List[HourlyWeatherPoint]
    temperature_unit: str
    precipitation_unit: str
    wind_speed_unit: str
    generated_at: str
