"""Radio-wave propagation (path loss) models.

References
----------
Hata, M. (1980). "Empirical formula for propagation loss in land mobile
radio services." IEEE Transactions on Vehicular Technology, 29(3), 317-325.

COST 231 Final Report (1999). "Digital Mobile Radio Towards Future
Generation Systems." European Commission, Directorate General
Telecommunications, Information Society, Chapter 4.

Rappaport, T. S. (2002). Wireless Communications: Principles and Practice
(2nd ed.). Prentice Hall.
"""

import math

__all__ = [
    "free_space_path_loss",
    "log_distance_path_loss",
    "okumura_hata",
    "cost231_hata",
]


def free_space_path_loss(distance_km: float, freq_mhz: float) -> float:
    """Free-space path loss (dB) between two isotropic antennas.

    Parameters
    ----------
    distance_km : float
        Distance between transmitter and receiver, in kilometres (> 0).
    freq_mhz : float
        Carrier frequency, in megahertz (> 0).

    Returns
    -------
    float
        Path loss in dB.
    """
    if distance_km <= 0:
        raise ValueError("distance_km must be positive")
    if freq_mhz <= 0:
        raise ValueError("freq_mhz must be positive")
    return 32.44 + 20 * math.log10(distance_km) + 20 * math.log10(freq_mhz)


def log_distance_path_loss(
    distance_km: float,
    freq_mhz: float,
    path_loss_exponent: float = 3.0,
    reference_distance_km: float = 1.0,
) -> float:
    """Log-distance path loss model (dB).

    PL(d) = PL(d0) + 10 * n * log10(d / d0), where PL(d0) is the
    free-space path loss at the reference distance d0.

    Parameters
    ----------
    distance_km : float
        Link distance, in kilometres (> 0).
    freq_mhz : float
        Carrier frequency, in megahertz (> 0).
    path_loss_exponent : float
        Environment-dependent exponent n (2.0 = free space, 2.7-3.5 =
        urban cellular, 4-6 = obstructed/indoor). Default 3.0.
    reference_distance_km : float
        Reference distance d0, in kilometres (> 0, <= distance_km).

    Returns
    -------
    float
        Path loss in dB.
    """
    if reference_distance_km <= 0:
        raise ValueError("reference_distance_km must be positive")
    if distance_km < reference_distance_km:
        raise ValueError("distance_km must be >= reference_distance_km")
    pl_d0 = free_space_path_loss(reference_distance_km, freq_mhz)
    return pl_d0 + 10 * path_loss_exponent * math.log10(
        distance_km / reference_distance_km
    )


def _hata_mobile_correction_medium_small_city(freq_mhz: float, hm_m: float) -> float:
    return (1.1 * math.log10(freq_mhz) - 0.7) * hm_m - (
        1.56 * math.log10(freq_mhz) - 0.8
    )


def _hata_mobile_correction_large_city(freq_mhz: float, hm_m: float) -> float:
    if freq_mhz <= 200:
        return 8.29 * (math.log10(1.54 * hm_m)) ** 2 - 1.1
    return 3.2 * (math.log10(11.75 * hm_m)) ** 2 - 4.97


def okumura_hata(
    freq_mhz: float,
    distance_km: float,
    base_station_height_m: float,
    mobile_height_m: float,
    environment: str = "urban",
    city_size: str = "medium_small",
) -> float:
    """Okumura-Hata median path loss (dB).

    Valid strictly for 150-1500 MHz, 1-20 km, base-station height
    30-200 m and mobile height 1-10 m; a ValueError is raised outside
    the frequency range since the model is not defined there.

    Parameters
    ----------
    freq_mhz : float
        Carrier frequency, 150-1500 MHz.
    distance_km : float
        Distance between base station and mobile, 1-20 km.
    base_station_height_m : float
        Effective base-station antenna height, 30-200 m.
    mobile_height_m : float
        Mobile/receiver antenna height, 1-10 m.
    environment : str
        One of "urban", "suburban", "open".
    city_size : str
        One of "medium_small", "large". Only affects the mobile-antenna
        height correction term used to derive the urban reference loss.

    Returns
    -------
    float
        Path loss in dB.
    """
    if not (150 <= freq_mhz <= 1500):
        raise ValueError("okumura_hata is only defined for 150-1500 MHz")
    if distance_km <= 0:
        raise ValueError("distance_km must be positive")

    f, d = freq_mhz, distance_km
    hb, hm = base_station_height_m, mobile_height_m

    if city_size == "large":
        a_hm = _hata_mobile_correction_large_city(f, hm)
    elif city_size == "medium_small":
        a_hm = _hata_mobile_correction_medium_small_city(f, hm)
    else:
        raise ValueError("city_size must be 'medium_small' or 'large'")

    base = 69.55 + 26.16 * math.log10(f) - 13.82 * math.log10(hb)
    l_urban = base - a_hm + (44.9 - 6.55 * math.log10(hb)) * math.log10(d)

    if environment == "urban":
        return l_urban
    if environment == "suburban":
        return l_urban - 2 * (math.log10(f / 28)) ** 2 - 5.4
    if environment == "open":
        return (
            l_urban
            - 4.78 * (math.log10(f)) ** 2
            + 18.33 * math.log10(f)
            - 40.94
        )
    raise ValueError("environment must be 'urban', 'suburban' or 'open'")


def cost231_hata(
    freq_mhz: float,
    distance_km: float,
    base_station_height_m: float,
    mobile_height_m: float,
    city_size: str = "medium",
) -> float:
    """COST-231 extension of the Hata model, for 1500-2000 MHz (dB).

    Parameters
    ----------
    freq_mhz : float
        Carrier frequency, 1500-2000 MHz.
    distance_km : float
        Distance between base station and mobile, 1-20 km.
    base_station_height_m : float
        Effective base-station antenna height, 30-200 m.
    mobile_height_m : float
        Mobile/receiver antenna height, 1-10 m.
    city_size : str
        One of "medium" (medium city / suburban, Cm = 0 dB) or
        "large" (metropolitan centre, Cm = 3 dB).

    Returns
    -------
    float
        Path loss in dB.
    """
    if not (1500 <= freq_mhz <= 2000):
        raise ValueError("cost231_hata is only defined for 1500-2000 MHz")
    if distance_km <= 0:
        raise ValueError("distance_km must be positive")

    f, d = freq_mhz, distance_km
    hb, hm = base_station_height_m, mobile_height_m
    a_hm = _hata_mobile_correction_medium_small_city(f, hm)

    if city_size == "large":
        c_m = 3.0
    elif city_size == "medium":
        c_m = 0.0
    else:
        raise ValueError("city_size must be 'medium' or 'large'")

    return (
        46.3
        + 33.9 * math.log10(f)
        - 13.82 * math.log10(hb)
        - a_hm
        + (44.9 - 6.55 * math.log10(hb)) * math.log10(d)
        + c_m
    )
