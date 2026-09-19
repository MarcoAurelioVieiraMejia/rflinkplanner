import math

import pytest

from rflinkplanner.propagation import (
    free_space_path_loss,
    log_distance_path_loss,
    okumura_hata,
    cost231_hata,
)


def test_free_space_path_loss_known_value():
    # Well-known reference figure: ~91.5 dB at 1 km / 900 MHz in free space.
    loss = free_space_path_loss(1.0, 900.0)
    assert loss == pytest.approx(91.53, abs=0.05)


def test_free_space_path_loss_scales_with_distance_and_frequency():
    base = free_space_path_loss(1.0, 900.0)
    assert free_space_path_loss(2.0, 900.0) == pytest.approx(base + 20 * math.log10(2))
    assert free_space_path_loss(1.0, 1800.0) == pytest.approx(base + 20 * math.log10(2))


def test_free_space_path_loss_rejects_invalid_input():
    with pytest.raises(ValueError):
        free_space_path_loss(0, 900.0)
    with pytest.raises(ValueError):
        free_space_path_loss(1.0, -1)


def test_log_distance_matches_free_space_at_reference_distance():
    loss = log_distance_path_loss(1.0, 900.0, path_loss_exponent=3.0, reference_distance_km=1.0)
    assert loss == pytest.approx(free_space_path_loss(1.0, 900.0))


def test_log_distance_rejects_distance_below_reference():
    with pytest.raises(ValueError):
        log_distance_path_loss(0.5, 900.0, reference_distance_km=1.0)


def test_okumura_hata_valid_frequency_range():
    with pytest.raises(ValueError):
        okumura_hata(2000, 5, 50, 1.5)
    with pytest.raises(ValueError):
        okumura_hata(100, 5, 50, 1.5)


def test_okumura_hata_environment_ordering():
    # For identical parameters, open terrain must show the least loss
    # and dense urban the most, since Hata builds suburban/open as
    # negative corrections on top of the urban reference loss.
    kwargs = dict(freq_mhz=900, distance_km=10, base_station_height_m=50, mobile_height_m=1.5)
    urban = okumura_hata(**kwargs, environment="urban")
    suburban = okumura_hata(**kwargs, environment="suburban")
    open_area = okumura_hata(**kwargs, environment="open")
    assert open_area < suburban < urban


def test_okumura_hata_increases_with_distance():
    kwargs = dict(freq_mhz=900, base_station_height_m=50, mobile_height_m=1.5, environment="urban")
    assert okumura_hata(distance_km=5, **kwargs) < okumura_hata(distance_km=10, **kwargs)


def test_okumura_hata_rejects_bad_environment_or_city_size():
    with pytest.raises(ValueError):
        okumura_hata(900, 5, 50, 1.5, environment="rural")
    with pytest.raises(ValueError):
        okumura_hata(900, 5, 50, 1.5, city_size="megacity")


def test_cost231_hata_valid_frequency_range():
    with pytest.raises(ValueError):
        cost231_hata(900, 5, 50, 1.5)
    with pytest.raises(ValueError):
        cost231_hata(2500, 5, 50, 1.5)


def test_cost231_hata_large_city_penalty():
    kwargs = dict(freq_mhz=1800, distance_km=5, base_station_height_m=50, mobile_height_m=1.5)
    medium = cost231_hata(**kwargs, city_size="medium")
    large = cost231_hata(**kwargs, city_size="large")
    assert large == pytest.approx(medium + 3.0)


def test_cost231_hata_increases_with_distance():
    kwargs = dict(freq_mhz=1800, base_station_height_m=50, mobile_height_m=1.5)
    assert cost231_hata(distance_km=5, **kwargs) < cost231_hata(distance_km=10, **kwargs)
