from __future__ import annotations
import math
from statistics import mean

EARTH_RADIUS_KM = 6371.0088


def fspl_db(distance_km: float, frequency_mhz: float) -> float:
    """Free Space Path Loss in dB, using distance in km and frequency in MHz."""
    distance_km = max(distance_km, 0.001)
    return 32.44 + 20 * math.log10(distance_km) + 20 * math.log10(frequency_mhz)


def received_power_dbm(distance_km: float, frequency_mhz: float, tx_power_dbm: float, gain_dbi: float) -> float:
    return tx_power_dbm + gain_dbi - fspl_db(distance_km, frequency_mhz)


def destination_point(lat: float, lon: float, bearing_deg: float, distance_km: float) -> tuple[float, float]:
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    bearing = math.radians(bearing_deg)
    angular_distance = distance_km / EARTH_RADIUS_KM

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), math.degrees(lon2)


def circle_coordinates(lat: float, lon: float, radius_km: float, points: int = 96) -> list[list[float]]:
    coords: list[list[float]] = []
    for i in range(points + 1):
        bearing = i * 360 / points
        p_lat, p_lon = destination_point(lat, lon, bearing, radius_km)
        coords.append([p_lon, p_lat])
    return coords


def classify_power(power_dbm: float, threshold_dbm: float) -> str:
    if power_dbm >= threshold_dbm + 25:
        return "excelente"
    if power_dbm >= threshold_dbm + 15:
        return "buena"
    if power_dbm >= threshold_dbm:
        return "limite"
    return "fuera_de_cobertura"


def coverage_geojson(
    lat: float,
    lon: float,
    frequency_mhz: float,
    tx_power_dbm: float,
    gain_dbi: float,
    radius_km: float,
    threshold_dbm: float,
    rings: int = 8,
) -> tuple[dict, dict]:
    features = []
    rx_values = []
    covered = 0

    # Outer to inner so the most useful close-range polygons remain visible when rendered.
    distances = [radius_km * i / rings for i in range(rings, 0, -1)]
    for distance_km in distances:
        rx = received_power_dbm(distance_km, frequency_mhz, tx_power_dbm, gain_dbi)
        rx_values.append(rx)
        if rx >= threshold_dbm:
            covered += 1
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "distance_km": round(distance_km, 3),
                    "rx_power_dbm": round(rx, 2),
                    "fspl_db": round(fspl_db(distance_km, frequency_mhz), 2),
                    "coverage_class": classify_power(rx, threshold_dbm),
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [circle_coordinates(lat, lon, distance_km)],
                },
            }
        )

    avg_rx = mean(rx_values) if rx_values else 0
    min_rx = min(rx_values) if rx_values else 0
    coverage_pct = covered / rings * 100 if rings else 0
    summary = {
        "modelo": "FSPL - Free Space Path Loss",
        "rsrp_promedio_dbm": round(avg_rx, 2),
        "rsrp_min_dbm": round(min_rx, 2),
        "cobertura_porcentaje": round(coverage_pct, 2),
        "radio_km": radius_km,
        "threshold_dbm": threshold_dbm,
        "nota": "Cálculo inicial sin altura de antena, relieve, clutter ni pérdidas adicionales.",
    }
    geojson = {"type": "FeatureCollection", "features": features}
    return summary, geojson
