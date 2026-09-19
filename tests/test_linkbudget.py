import pytest

from rflinkplanner.linkbudget import compute_link_budget


def test_link_budget_basic_arithmetic():
    result = compute_link_budget(
        tx_power_dbm=20.0,
        tx_antenna_gain_dbi=24.0,
        rx_antenna_gain_dbi=24.0,
        path_loss_db=130.0,
        rx_sensitivity_dbm=-85.0,
        tx_cable_loss_db=1.0,
        rx_cable_loss_db=1.0,
        other_losses_db=2.0,
    )
    # EIRP = 20 - 1 + 24 = 43
    assert result.eirp_dbm == pytest.approx(43.0)
    # Received = 43 - 130 - 2 + 24 - 1 = -66
    assert result.received_power_dbm == pytest.approx(-66.0)
    # Fade margin = -66 - (-85) = 19
    assert result.fade_margin_db == pytest.approx(19.0)
    assert result.link_closed is True


def test_link_budget_flags_closed_link_at_zero_margin():
    result = compute_link_budget(
        tx_power_dbm=0.0,
        tx_antenna_gain_dbi=0.0,
        rx_antenna_gain_dbi=0.0,
        path_loss_db=100.0,
        rx_sensitivity_dbm=-100.0,
    )
    assert result.fade_margin_db == pytest.approx(0.0)
    assert result.link_closed is True


def test_link_budget_flags_unclosed_link():
    result = compute_link_budget(
        tx_power_dbm=10.0,
        tx_antenna_gain_dbi=10.0,
        rx_antenna_gain_dbi=10.0,
        path_loss_db=150.0,
        rx_sensitivity_dbm=-90.0,
    )
    assert result.fade_margin_db < 0
    assert result.link_closed is False
