import OAuthProvider from "@cloudflare/workers-oauth-provider";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { McpAgent } from "agents/mcp";
import { z } from "zod";
import { GitHubHandler } from "./github-handler";
import {
	CurrentWeather,
	WeatherForecast,
	HourlyForecast,
	WeatherAlerts
} from "./weather-types";
import { searchLocations, getWeatherData } from "./weather-api";
import { resolveLocation } from "./location-resolver";
import {
	weatherCodeToDescription,
	MAX_FORECAST_DAYS,
	MAX_FORECAST_HOURS,
	HIGH_WIND_THRESHOLD_KMH,
	SEVERE_WEATHER_CODES,
	FREEZING_RAIN_CODES,
	SNOW_CODES
} from "./weather-config";

// Context from the auth process, encrypted & stored in the auth token
// and provided to the DurableMCP as this.props
type Props = {
	login: string;
	name: string;
	email: string;
	accessToken: string;
};

const ALLOWED_USERNAMES = new Set<string>([
	// Add GitHub usernames of users who should have access to the image generation tool
	// For example: 'yourusername', 'coworkerusername'
]);

export class MyMCP extends McpAgent<Env, Record<string, never>, Props> {
	server = new McpServer({
		name: "Weather Lookup",
		version: "1.0.0",
	});

	async init() {
		// Search for locations by name or postal code
		this.server.tool(
			"search_locations_tool",
			"Search for locations by name or postal code.",
			{
				location_name: z.string().describe("Name of city, region, or postal code to search for"),
				limit: z.number().min(1).max(10).default(5).describe("Maximum number of results to return (1-10, default 5)")
			},
			async ({ location_name, limit }) => {
				if (location_name.trim().length < 2) {
					throw new Error("Location name must be at least 2 characters long.");
				}

				const clampedLimit = Math.max(1, Math.min(limit, 10));
				const locations = await searchLocations(location_name, clampedLimit);

				return {
					content: [{ text: JSON.stringify(locations, null, 2), type: "text" }],
				};
			}
		);

		// Get current weather conditions for a location
		this.server.tool(
			"get_current_weather",
			"Get current weather conditions for a location.",
			{
				location_name: z.string().describe("Name of the location (city, region, etc.)"),
				temperature_unit: z.string().default("celsius").describe('Temperature unit ("celsius" or "fahrenheit")')
			},
			async ({ location_name, temperature_unit }) => {
				const location = await resolveLocation(location_name);

				const currentParams = [
					"temperature_2m", "relative_humidity_2m", "weather_code",
					"wind_speed_10m", "wind_direction_10m", "pressure_msl", "cloud_cover"
				];

				const weatherData = await getWeatherData(
					location.latitude,
					location.longitude,
					{
						current: currentParams,
						temperatureUnit: temperature_unit
					}
				);

				const current = weatherData.current!;
				const currentUnits = weatherData.current_units!;

				const result: CurrentWeather = {
					location,
					temperature: current.temperature_2m,
					temperature_unit: currentUnits.temperature_2m,
					humidity: current.relative_humidity_2m,
					weather_description: weatherCodeToDescription(current.weather_code),
					weather_code: current.weather_code,
					wind_speed: current.wind_speed_10m,
					wind_direction: current.wind_direction_10m,
					wind_speed_unit: currentUnits.wind_speed_10m,
					pressure: current.pressure_msl,
					cloud_cover: current.cloud_cover,
					timestamp: current.time
				};

				return {
					content: [{ text: JSON.stringify(result, null, 2), type: "text" }],
				};
			}
		);

		// Get daily weather forecast for a location
		this.server.tool(
			"get_weather_forecast",
			"Get daily weather forecast for a location.",
			{
				location_name: z.string().describe("Name of the location (city, region, etc.)"),
				forecast_days: z.number().min(1).max(16).default(7).describe("Number of forecast days (1-16, default 7)"),
				temperature_unit: z.string().default("celsius").describe('Temperature unit ("celsius" or "fahrenheit")')
			},
			async ({ location_name, forecast_days, temperature_unit }) => {
				const location = await resolveLocation(location_name);
				const clampedDays = Math.max(1, Math.min(forecast_days, MAX_FORECAST_DAYS));

				const dailyParams = [
					"temperature_2m_max", "temperature_2m_min", "weather_code",
					"precipitation_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"
				];

				const weatherData = await getWeatherData(
					location.latitude,
					location.longitude,
					{
						daily: dailyParams,
						forecastDays: clampedDays,
						temperatureUnit: temperature_unit
					}
				);

				const daily = weatherData.daily!;
				const dailyUnits = weatherData.daily_units!;

				const forecastDays = daily.time.map((time: string, i: number) => ({
					date: time,
					temperature_max: daily.temperature_2m_max[i],
					temperature_min: daily.temperature_2m_min[i],
					temperature_unit: dailyUnits.temperature_2m_max,
					weather_description: weatherCodeToDescription(daily.weather_code[i]),
					weather_code: daily.weather_code[i],
					precipitation_sum: daily.precipitation_sum[i],
					precipitation_unit: dailyUnits.precipitation_sum,
					wind_speed_max: daily.wind_speed_10m_max[i],
					wind_direction_dominant: daily.wind_direction_10m_dominant[i],
					wind_speed_unit: dailyUnits.wind_speed_10m_max
				}));

				const result: WeatherForecast = {
					location,
					forecast_days: forecastDays,
					generated_at: new Date().toISOString()
				};

				return {
					content: [{ text: JSON.stringify(result, null, 2), type: "text" }],
				};
			}
		);

		// Get hourly weather forecast for a location
		this.server.tool(
			"get_hourly_forecast",
			"Get hourly weather forecast for a location.",
			{
				location_name: z.string().describe("Name of the location (city, region, etc.)"),
				forecast_hours: z.number().min(1).max(168).default(24).describe("Number of forecast hours (1-168, default 24)"),
				temperature_unit: z.string().default("celsius").describe('Temperature unit ("celsius" or "fahrenheit")')
			},
			async ({ location_name, forecast_hours, temperature_unit }) => {
				const location = await resolveLocation(location_name);
				const clampedHours = Math.max(1, Math.min(forecast_hours, MAX_FORECAST_HOURS));

				const hourlyParams = [
					"temperature_2m", "relative_humidity_2m", "weather_code",
					"precipitation", "wind_speed_10m", "wind_direction_10m", "cloud_cover"
				];

				const weatherData = await getWeatherData(
					location.latitude,
					location.longitude,
					{
						hourly: hourlyParams,
						temperatureUnit: temperature_unit
					}
				);

				const hourly = weatherData.hourly!;
				const hourlyUnits = weatherData.hourly_units!;

				// Limit to requested hours
				const hourlyData = [];
				for (let i = 0; i < Math.min(clampedHours, hourly.time.length); i++) {
					hourlyData.push({
						time: hourly.time[i],
						temperature: hourly.temperature_2m[i],
						humidity: hourly.relative_humidity_2m[i],
						weather_code: hourly.weather_code[i],
						weather_description: weatherCodeToDescription(hourly.weather_code[i]),
						precipitation: hourly.precipitation[i],
						wind_speed: hourly.wind_speed_10m[i],
						wind_direction: hourly.wind_direction_10m[i],
						cloud_cover: hourly.cloud_cover[i]
					});
				}

				const result: HourlyForecast = {
					location,
					hourly_data: hourlyData,
					temperature_unit: hourlyUnits.temperature_2m,
					precipitation_unit: hourlyUnits.precipitation,
					wind_speed_unit: hourlyUnits.wind_speed_10m,
					generated_at: new Date().toISOString()
				};

				return {
					content: [{ text: JSON.stringify(result, null, 2), type: "text" }],
				};
			}
		);

		// Check for severe weather conditions and alerts for a location
		this.server.tool(
			"get_weather_alerts",
			"Check for severe weather conditions and alerts for a location.",
			{
				location_name: z.string().describe("Name of the location (city, region, etc.)")
			},
			async ({ location_name }) => {
				const location = await resolveLocation(location_name);

				// Get current and near-term forecast for alert analysis
				const currentParams = ["temperature_2m", "weather_code", "wind_speed_10m", "precipitation"];
				const hourlyParams = ["temperature_2m", "weather_code", "wind_speed_10m", "precipitation", "wind_gusts_10m"];

				const weatherData = await getWeatherData(
					location.latitude,
					location.longitude,
					{
						current: currentParams,
						hourly: hourlyParams,
						forecastDays: 2 // Check next 48 hours
					}
				);

				const alerts = [];
				const current = weatherData.current!;
				const hourly = weatherData.hourly!;

				// Check for severe weather conditions
				const currentWeatherCode = current.weather_code;
				if (SEVERE_WEATHER_CODES.includes(currentWeatherCode)) {
					alerts.push({
						type: "severe_weather",
						severity: "high",
						title: "Thunderstorm Warning",
						description: weatherCodeToDescription(currentWeatherCode),
						time: "current"
					});
				} else if (FREEZING_RAIN_CODES.includes(currentWeatherCode)) {
					alerts.push({
						type: "severe_weather",
						severity: "high",
						title: "Freezing Rain Warning",
						description: weatherCodeToDescription(currentWeatherCode),
						time: "current"
					});
				} else if (SNOW_CODES.includes(currentWeatherCode)) {
					alerts.push({
						type: "weather_advisory",
						severity: "medium",
						title: "Snow Advisory",
						description: weatherCodeToDescription(currentWeatherCode),
						time: "current"
					});
				}

				// Check wind conditions
				const currentWind = current.wind_speed_10m;
				if (currentWind > HIGH_WIND_THRESHOLD_KMH) {
					alerts.push({
						type: "wind_warning",
						severity: "medium",
						title: "High Wind Warning",
						description: `Strong winds at ${currentWind} km/h`,
						time: "current"
					});
				}

				// Check for upcoming severe weather in next 24 hours
				for (let i = 0; i < Math.min(24, hourly.time.length); i++) {
					const weatherCode = hourly.weather_code[i];
					if (SEVERE_WEATHER_CODES.includes(weatherCode) && !alerts.some(alert => alert.type === "severe_weather")) {
						alerts.push({
							type: "severe_weather",
							severity: "medium",
							title: "Incoming Thunderstorm",
							description: `Thunderstorm expected at ${hourly.time[i]}`,
							time: hourly.time[i]
						});
						break;
					}
				}

				const result: WeatherAlerts = {
					location,
					alerts,
					alert_count: alerts.length,
					checked_at: new Date().toISOString()
				};

				return {
					content: [{ text: JSON.stringify(result, null, 2), type: "text" }],
				};
			}
		);

		// Dynamically add tools based on the user's login. In this case, I want to limit
		// access to my Image Generation tool to just me
		if (ALLOWED_USERNAMES.has(this.props.login)) {
			this.server.tool(
				"generateImage",
				"Generate an image using the `flux-1-schnell` model. Works best with 8 steps.",
				{
					prompt: z
						.string()
						.describe("A text description of the image you want to generate."),
					steps: z
						.number()
						.min(4)
						.max(8)
						.default(4)
						.describe(
							"The number of diffusion steps; higher values can improve quality but take longer. Must be between 4 and 8, inclusive.",
						),
				},
				async ({ prompt, steps }) => {
					const response = await this.env.AI.run("@cf/black-forest-labs/flux-1-schnell", {
						prompt,
						steps,
					});

					return {
						content: [{ data: response.image!, mimeType: "image/jpeg", type: "image" }],
					};
				},
			);
		}

	}
}

export default new OAuthProvider({
	apiHandler: MyMCP.mount("/sse") as any,
	apiRoute: "/sse",
	authorizeEndpoint: "/authorize",
	clientRegistrationEndpoint: "/register",
	defaultHandler: GitHubHandler as any,
	tokenEndpoint: "/token",
});
