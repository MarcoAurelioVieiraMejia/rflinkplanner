import pytest

from rflinkplanner.fresnel import (
    fresnel_zone_radius,
    earth_curvature_bulge,
    clearance_profile,
)


def test_fresnel_zone_radius_known_value():
    # f = 2.4 GHz, d1 = d2 = 5 km -> wavelength = c / f = 0.12491 m
    # r1 = sqrt(1 * 0.12491 * 2_500_000 / 10_000) = sqrt(0.12491 * 2500) ~= 17.67 m
    radius = fresnel_zone_radius(5.0, 5.0, 2.4, zone=1)
    assert radius == pytest.approx(17.67, abs=0.05)


def test_fresnel_zone_radius_grows_with_zone_number():
    r1 = fresnel_zone_radius(5.0, 5.0, 2.4, zone=1)
    r2 = fresnel_zone_radius(5.0, 5.0, 2.4, zone=2)
    assert r2 == pytest.approx(r1 * (2 ** 0.5))


def test_fresnel_zone_radius_shrinks_with_frequency():
    low = fresnel_zone_radius(5.0, 5.0, 0.9, zone=1)
    high = fresnel_zone_radius(5.0, 5.0, 5.8, zone=1)
    assert high < low


def test_fresnel_zone_radius_rejects_invalid_input():
    with pytest.raises(ValueError):
        fresnel_zone_radius(0, 5.0, 2.4)
    with pytest.raises(ValueError):
        fresnel_zone_radius(5.0, 5.0, 2.4, zone=0)


def test_earth_curvature_bulge_known_value():
    # d1 = d2 = 10 km, k = 4/3 -> R_eff = 8494.667 km
    # bulge = (10*10) / (2*8494.667) * 1000 ~= 5.886 m
    bulge = earth_curvature_bulge(10.0, 10.0, k_factor=4 / 3)
    assert bulge == pytest.approx(5.886, abs=0.01)


def test_earth_curvature_bulge_zero_at_endpoints():
    assert earth_curvature_bulge(0.0, 20.0) == 0.0
    assert earth_curvature_bulge(20.0, 0.0) == 0.0


def test_clearance_profile_flags_obstruction():
    # Flat 10 km link at 2 m height, with a 30 m tower in the middle:
    # the line of sight passes at ~2 m, so the mast must obstruct it.
    terrain = [(0.0, 0.0), (5.0, 30.0), (10.0, 0.0)]
    profile = clearance_profile(
        terrain, tx_height_m=2.0, rx_height_m=2.0, freq_ghz=5.8
    )
    midpoint = next(p for p in profile if p["distance_km"] == 5.0)
    assert midpoint["obstructed"] is True


def test_clearance_profile_clear_flat_link():
    # Flat 10 km link, tall masts at both ends -> should be clear.
    terrain = [(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)]
    profile = clearance_profile(
        terrain, tx_height_m=30.0, rx_height_m=30.0, freq_ghz=5.8
    )
    assert all(not p["obstructed"] for p in profile)


def test_clearance_profile_requires_at_least_two_points():
    with pytest.raises(ValueError):
        clearance_profile([(0.0, 0.0)], tx_height_m=10, rx_height_m=10, freq_ghz=5.8)
