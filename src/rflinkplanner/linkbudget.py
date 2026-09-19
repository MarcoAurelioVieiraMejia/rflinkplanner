"""End-to-end RF link-budget calculation."""

from dataclasses import dataclass

__all__ = ["LinkBudgetResult", "compute_link_budget"]


@dataclass(frozen=True)
class LinkBudgetResult:
    """Result of a link-budget calculation.

    Attributes
    ----------
    eirp_dbm : float
        Effective isotropic radiated power at the transmitter.
    received_power_dbm : float
        Signal power at the receiver input.
    fade_margin_db : float
        Margin between received power and receiver sensitivity.
        Positive means the link closes; negative means it does not.
    link_closed : bool
        True if fade_margin_db >= 0.
    """

    eirp_dbm: float
    received_power_dbm: float
    fade_margin_db: float
    link_closed: bool


def compute_link_budget(
    tx_power_dbm: float,
    tx_antenna_gain_dbi: float,
    rx_antenna_gain_dbi: float,
    path_loss_db: float,
    rx_sensitivity_dbm: float,
    tx_cable_loss_db: float = 0.0,
    rx_cable_loss_db: float = 0.0,
    other_losses_db: float = 0.0,
) -> LinkBudgetResult:
    """Compute a full link budget from transmitter to receiver.

    EIRP = tx_power - tx_cable_loss + tx_antenna_gain
    Received power = EIRP - path_loss - other_losses
                      + rx_antenna_gain - rx_cable_loss
    Fade margin = received power - rx_sensitivity

    Parameters
    ----------
    tx_power_dbm : float
        Transmitter output power, in dBm.
    tx_antenna_gain_dbi, rx_antenna_gain_dbi : float
        Antenna gains at each end, in dBi.
    path_loss_db : float
        Path loss between the antennas, in dB (e.g. from
        ``rflinkplanner.propagation`` or ``fresnel``).
    rx_sensitivity_dbm : float
        Receiver sensitivity threshold, in dBm.
    tx_cable_loss_db, rx_cable_loss_db : float
        Feeder/connector losses at each end, in dB.
    other_losses_db : float
        Additional losses to account for (rain attenuation,
        polarization mismatch, fade allowance, etc.), in dB.

    Returns
    -------
    LinkBudgetResult
    """
    eirp_dbm = tx_power_dbm - tx_cable_loss_db + tx_antenna_gain_dbi
    received_power_dbm = (
        eirp_dbm - path_loss_db - other_losses_db + rx_antenna_gain_dbi - rx_cable_loss_db
    )
    fade_margin_db = received_power_dbm - rx_sensitivity_dbm

    return LinkBudgetResult(
        eirp_dbm=eirp_dbm,
        received_power_dbm=received_power_dbm,
        fade_margin_db=fade_margin_db,
        link_closed=fade_margin_db >= 0,
    )
