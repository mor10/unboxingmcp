/**
 * API client for interacting with Open-Meteo services
 */

import { LocationInfo } from "./weather-types";
import { GEOCODING_API_URL, WEATHER_API_URL, MAX_LOCATION_SEARCH_RESULTS } from "./weather-config";

interface LocationSearchResult {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  country?: string;
  admin1?: string;
  admin2?: string;
  timezone: string;
  population?: number;
  elevation?: number;
}

interface GeoccodingResponse {
  results?: LocationSearchResult[];
  reason?: string;
}

interface WeatherApiResponse {
  current?: Record<string, any>;
  current_units?: Record<string, string>;
  hourly?: Record<string, any[]>;
  hourly_units?: Record<string, string>;
  daily?: Record<string, any[]>;
  daily_units?: Record<string, string>;
  reason?: string;
}

/**
 * Search for locations using the geocoding API
 */
export async function searchLocations(locationName: string, limit: number = 10): Promise<LocationInfo[]> {
  const params = new URLSearchParams({
    name: locationName,
    count: Math.min(limit, MAX_LOCATION_SEARCH_RESULTS).toString(),
    format: "json",
  });

  const response = await fetch(`${GEOCODING_API_URL}?${params}`);

  if (!response.ok) {
    const errorData = await response.json() as GeoccodingResponse;
    throw new Error(`Geocoding API error: ${errorData.reason || 'Unknown error'}`);
  }

  const data = await response.json() as GeoccodingResponse;
  const results = data.results || [];

  return results.map(loc => ({
    id: loc.id,
    name: loc.name,
    latitude: loc.latitude,
    longitude: loc.longitude,
    country: loc.country || "",
    admin1: loc.admin1,
    admin2: loc.admin2,
    timezone: loc.timezone,
    population: loc.population,
    elevation: loc.elevation,
  }));
}

/**
 * Get weather data from Open-Meteo forecast API
 */
export async function getWeatherData(
  latitude: number,
  longitude: number,
  options: {
    current?: string[];
    hourly?: string[];
    daily?: string[];
    forecastDays?: number;
    temperatureUnit?: string;
    windSpeedUnit?: string;
    precipitationUnit?: string;
  } = {}
): Promise<WeatherApiResponse> {
  const {
    current,
    hourly,
    daily,
    forecastDays = 7,
    temperatureUnit = "celsius",
    windSpeedUnit = "kmh",
    precipitationUnit = "mm",
  } = options;

  const params = new URLSearchParams({
    latitude: latitude.toString(),
    longitude: longitude.toString(),
    temperature_unit: temperatureUnit,
    wind_speed_unit: windSpeedUnit,
    precipitation_unit: precipitationUnit,
    forecast_days: forecastDays.toString(),
  });

  if (current) {
    params.set("current", current.join(","));
  }
  if (hourly) {
    params.set("hourly", hourly.join(","));
  }
  if (daily) {
    params.set("daily", daily.join(","));
  }

  const response = await fetch(`${WEATHER_API_URL}?${params}`);

  if (!response.ok) {
    const errorData = await response.json() as WeatherApiResponse;
    throw new Error(`Weather API error: ${errorData.reason || 'Unknown error'}`);
  }

  return await response.json() as WeatherApiResponse;
}
