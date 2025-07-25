/**
 * Location resolution and disambiguation logic
 */

import { LocationInfo } from "./weather-types";
import { searchLocations } from "./weather-api";

/**
 * Resolve a location name to coordinates, returning the first location when multiple are found
 */
export async function resolveLocation(locationName: string): Promise<LocationInfo> {
  const locations = await searchLocations(locationName, 10);

  if (locations.length === 0) {
    throw new Error(
      `No locations found for '${locationName}'. Please try a different search term.`
    );
  }

  // Always use the first result (most relevant according to the API)
  return locations[0];
}
