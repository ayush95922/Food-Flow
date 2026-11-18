"""Geographic helpers. All travel figures produced here are SIMULATED estimates
(great-circle distance x detour factor / assumed speed), not real road data."""
import math
from typing import Tuple

EARTH_RADIUS_KM = 6371.0088


def haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(h)))


def road_distance_km(a, b, detour_factor: float = 1.3) -> float:
    """Simulated road distance = straight-line distance x detour factor (assumption)."""
    return haversine_km(a, b) * detour_factor


def travel_minutes(distance_km: float, speed_kmph: float = 25.0) -> float:
    if speed_kmph <= 0:
        raise ValueError("speed must be positive")
    return distance_km / speed_kmph * 60.0
