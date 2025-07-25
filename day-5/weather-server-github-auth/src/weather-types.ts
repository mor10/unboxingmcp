/**
 * TypeScript interfaces for weather data models
 */

export interface LocationInfo {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  admin1?: string; // State/Province
  admin2?: string; // County/Region
  timezone: string;
  population?: number;
  elevation?: number;
}

export interface CurrentWeather {
  location: LocationInfo;
  temperature: number;
  temperature_unit: string;
  humidity: number;
  weather_description: string;
  weather_code: number;
  wind_speed: number;
  wind_direction: number;
  wind_speed_unit: string;
  pressure: number;
  cloud_cover: number;
  timestamp: string;
}

export interface DailyForecast {
  date: string;
  temperature_max: number;
  temperature_min: number;
  temperature_unit: string;
  weather_description: string;
  weather_code: number;
  precipitation_sum: number;
  precipitation_unit: string;
  wind_speed_max: number;
  wind_direction_dominant: number;
  wind_speed_unit: string;
}

export interface WeatherForecast {
  location: LocationInfo;
  forecast_days: DailyForecast[];
  generated_at: string;
}

export interface HourlyWeatherPoint {
  time: string;
  temperature: number;
  humidity: number;
  weather_code: number;
  weather_description: string;
  precipitation: number;
  wind_speed: number;
  wind_direction: number;
  cloud_cover: number;
}

export interface HourlyForecast {
  location: LocationInfo;
  hourly_data: HourlyWeatherPoint[];
  temperature_unit: string;
  precipitation_unit: string;
  wind_speed_unit: string;
  generated_at: string;
}

export interface WeatherAlert {
  type: string;
  severity: string;
  title: string;
  description: string;
  time: string;
}

export interface WeatherAlerts {
  location: LocationInfo;
  alerts: WeatherAlert[];
  alert_count: number;
  checked_at: string;
}
