"""Fresnel-zone clearance and earth-curvature bulge calculations for
point-to-point line-of-sight link planning.
"""

import math

SPEED_OF_LIGHT_M_S = 299_792_458.0
EARTH_RADIUS_KM = 6371.0

__all__ = [
    "fresnel_zone_radius",
    "earth_curvature_bulge",
    "clearance_profile",
]


def fresnel_zone_radius(d1_km: float, d2_km: float, freq_ghz: float, zone: int = 1) -> float:
    """Radius (m) of the n-th Fresnel zone at a point along a link.

    r_n = sqrt(n * lambda * d1 * d2 / (d1 + d2))

    Parameters
    ----------
    d1_km, d2_km : float
        Distance from the point to each end of the link, in kilometres
        (both > 0; d1 + d2 = total link distance).
    freq_ghz : float
        Carrier frequency, in gigahertz (> 0).
    zone : int
        Fresnel zone number (>= 1). The first zone (default) is the one
        that matters for clearance planning.

    Returns
    -------
    float
        Fresnel zone radius, in metres.
    """
    if d1_km <= 0 or d2_km <= 0:
        raise ValueError("d1_km and d2_km must be positive")
    if freq_ghz <= 0:
        raise ValueError("freq_ghz must be positive")
    if zone < 1:
        raise ValueError("zone must be >= 1")

    wavelength_m = SPEED_OF_LIGHT_M_S / (freq_ghz * 1e9)
    d1_m, d2_m = d1_km * 1000.0, d2_km * 1000.0
    return math.sqrt(zone * wavelength_m * d1_m * d2_m / (d1_m + d2_m))


def earth_curvature_bulge(d1_km: float, d2_km: float, k_factor: float = 4 / 3) -> float:
    """Earth-curvature bulge height (m) at a point along a link.

    Uses the effective earth-radius approximation R_eff = k * R_earth,
    which folds atmospheric refraction into an equivalent earth radius.
    k = 4/3 is the standard median value for terrestrial microwave links.

    Parameters
    ----------
    d1_km, d2_km : float
        Distance from the point to each end of the link, in kilometres.
    k_factor : float
        Effective earth-radius factor (default 4/3).

    Returns
    -------
    float
        Bulge height, in metres, that the line of sight loses to
        earth curvature at this point.
    """
    if d1_km < 0 or d2_km < 0:
        raise ValueError("d1_km and d2_km must be non-negative")
    if k_factor <= 0:
        raise ValueError("k_factor must be positive")

    r_eff_km = k_factor * EARTH_RADIUS_KM
    return (d1_km * d2_km) / (2 * r_eff_km) * 1000.0


def clearance_profile(
    terrain_profile,
    tx_height_m: float,
    rx_height_m: float,
    freq_ghz: float,
    k_factor: float = 4 / 3,
    zone_fraction: float = 0.6,
):
    """Line-of-sight clearance check along a terrain profile.

    Parameters
    ----------
    terrain_profile : sequence of (distance_km, elevation_m)
        Ground elevation samples from the transmitter (distance 0) to
        the receiver (distance = total link length), sorted ascending
        by distance. At least two points are required.
    tx_height_m, rx_height_m : float
        Antenna height above ground at each end, in metres.
    freq_ghz : float
        Carrier frequency, in gigahertz.
    k_factor : float
        Effective earth-radius factor (default 4/3).
    zone_fraction : float
        Fraction of the first Fresnel zone that must remain clear of
        obstructions for the link to be considered reliable. 0.6 is
        the standard planning threshold.

    Returns
    -------
    list of dict
        One entry per input profile point, each with: distance_km,
        line_of_sight_height_m, earth_bulge_m, fresnel_radius_m,
        required_clearance_m, actual_clearance_m, obstructed (bool).
    """
    if len(terrain_profile) < 2:
        raise ValueError("terrain_profile needs at least two points")

    points = sorted(terrain_profile, key=lambda p: p[0])
    d_total = points[-1][0]
    if d_total <= 0:
        raise ValueError("total link distance must be positive")

    tx_elev = points[0][1] + tx_height_m
    rx_elev = points[-1][1] + rx_height_m

    results = []
    for distance_km, ground_elev_m in points:
        d1 = distance_km
        d2 = d_total - distance_km

        los_height = tx_elev + (rx_elev - tx_elev) * (d1 / d_total)

        if d1 == 0 or d2 == 0:
            fresnel_radius_m = 0.0
            bulge_m = 0.0
        else:
            fresnel_radius_m = fresnel_zone_radius(d1, d2, freq_ghz, zone=1)
            bulge_m = earth_curvature_bulge(d1, d2, k_factor)

        effective_los = los_height - bulge_m
        required_clearance_m = zone_fraction * fresnel_radius_m
        actual_clearance_m = effective_los - ground_elev_m

        results.append(
            {
                "distance_km": distance_km,
                "line_of_sight_height_m": los_height,
                "earth_bulge_m": bulge_m,
                "fresnel_radius_m": fresnel_radius_m,
                "required_clearance_m": required_clearance_m,
                "actual_clearance_m": actual_clearance_m,
                "obstructed": actual_clearance_m < required_clearance_m,
            }
        )
    return results
