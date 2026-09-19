"""Worked example: planning a 12 km point-to-point rural connectivity
link at 5.8 GHz, from path-loss estimation through Fresnel clearance to
the final link budget.

Run with:  python examples/rural_link_example.py
"""

from rflinkplanner import (
    log_distance_path_loss,
    clearance_profile,
    compute_link_budget,
)

FREQ_GHZ = 5.8
FREQ_MHZ = FREQ_GHZ * 1000
DISTANCE_KM = 12.0

# Simplified terrain profile: (distance_km, ground_elevation_m).
# In practice this would come from a digital elevation model (e.g. SRTM).
TERRAIN_PROFILE = [
    (0.0, 1200.0),
    (3.0, 1215.0),
    (6.0, 1260.0),  # a hill roughly midway
    (9.0, 1220.0),
    (12.0, 1180.0),
]

TX_HEIGHT_M = 15.0
RX_HEIGHT_M = 12.0


def main():
    path_loss_db = log_distance_path_loss(
        DISTANCE_KM, FREQ_MHZ, path_loss_exponent=2.2
    )
    print(f"Estimated path loss over {DISTANCE_KM} km at {FREQ_GHZ} GHz: "
          f"{path_loss_db:.1f} dB")

    profile = clearance_profile(
        TERRAIN_PROFILE, TX_HEIGHT_M, RX_HEIGHT_M, FREQ_GHZ
    )
    print("\nClearance profile:")
    for point in profile:
        status = "OBSTRUCTED" if point["obstructed"] else "clear"
        print(
            f"  d={point['distance_km']:5.1f} km  "
            f"clearance={point['actual_clearance_m']:7.2f} m  "
            f"required={point['required_clearance_m']:6.2f} m  [{status}]"
        )

    if any(p["obstructed"] for p in profile):
        print("\nWarning: line of sight is obstructed; raise tower heights "
              "or relocate the hop before proceeding to the link budget.")

    budget = compute_link_budget(
        tx_power_dbm=23.0,
        tx_antenna_gain_dbi=24.0,
        rx_antenna_gain_dbi=24.0,
        path_loss_db=path_loss_db,
        rx_sensitivity_dbm=-88.0,
        tx_cable_loss_db=1.5,
        rx_cable_loss_db=1.5,
        other_losses_db=2.0,
    )
    print(f"\nEIRP: {budget.eirp_dbm:.1f} dBm")
    print(f"Received power: {budget.received_power_dbm:.1f} dBm")
    print(f"Fade margin: {budget.fade_margin_db:.1f} dB")
    print(f"Link closed: {budget.link_closed}")


if __name__ == "__main__":
    main()
