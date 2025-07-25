/**
 * Configuration settings for the Open-Meteo Weather MCP Server
 */

// API Endpoints
export const GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search";
export const WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast";

// Default Parameters
export const DEFAULT_TEMPERATURE_UNIT = "celsius";
export const DEFAULT_WIND_SPEED_UNIT = "kmh";
export const DEFAULT_PRECIPITATION_UNIT = "mm";
export const DEFAULT_FORECAST_DAYS = 7;
export const DEFAULT_FORECAST_HOURS = 24;
export const MAX_FORECAST_DAYS = 16;
export const MAX_FORECAST_HOURS = 168;
export const MAX_LOCATION_SEARCH_RESULTS = 100;

// Weather Alert Thresholds
export const HIGH_WIND_THRESHOLD_KMH = 50; // km/h
export const SEVERE_WEATHER_CODES = [95, 96, 99]; // Thunderstorms
export const FREEZING_RAIN_CODES = [66, 67];
export const SNOW_CODES = [71, 73, 75];

// Weather code descriptions (WMO codes)
export const WEATHER_CODES: Record<number, string> = {
  0: "Clear sky",
  1: "Mainly clear",
  2: "Partly cloudy",
  3: "Overcast",
  45: "Fog",
  48: "Depositing rime fog",
  51: "Light drizzle",
  53: "Moderate drizzle",
  55: "Dense drizzle",
  56: "Light freezing drizzle",
  57: "Dense freezing drizzle",
  61: "Slight rain",
  63: "Moderate rain",
  65: "Heavy rain",
  66: "Light freezing rain",
  67: "Heavy freezing rain",
  71: "Slight snow fall",
  73: "Moderate snow fall",
  75: "Heavy snow fall",
  77: "Snow grains",
  80: "Slight rain showers",
  81: "Moderate rain showers",
  82: "Violent rain showers",
  85: "Slight snow showers",
  86: "Heavy snow showers",
  95: "Thunderstorm",
  96: "Thunderstorm with slight hail",
  99: "Thunderstorm with heavy hail",
};

/**
 * Convert WMO weather code to human readable description
 */
export function weatherCodeToDescription(code: number): string {
  return WEATHER_CODES[code] || `Unknown weather condition (code: ${code})`;
}
