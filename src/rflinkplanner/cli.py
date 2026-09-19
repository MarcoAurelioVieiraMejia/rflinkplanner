"""Command-line interface for rflinkplanner."""

import argparse
import sys

from .propagation import free_space_path_loss, okumura_hata, cost231_hata
from .fresnel import fresnel_zone_radius
from .linkbudget import compute_link_budget


def _cmd_fspl(args):
    loss = free_space_path_loss(args.distance_km, args.freq_mhz)
    print(f"Free-space path loss: {loss:.2f} dB")


def _cmd_hata(args):
    loss = okumura_hata(
        args.freq_mhz,
        args.distance_km,
        args.tx_height_m,
        args.rx_height_m,
        environment=args.environment,
        city_size=args.city_size,
    )
    print(f"Okumura-Hata path loss: {loss:.2f} dB")


def _cmd_cost231(args):
    loss = cost231_hata(
        args.freq_mhz,
        args.distance_km,
        args.tx_height_m,
        args.rx_height_m,
        city_size=args.city_size,
    )
    print(f"COST-231 Hata path loss: {loss:.2f} dB")


def _cmd_fresnel(args):
    radius = fresnel_zone_radius(args.d1_km, args.d2_km, args.freq_ghz, zone=args.zone)
    print(f"Fresnel zone {args.zone} radius: {radius:.2f} m")


def _cmd_linkbudget(args):
    result = compute_link_budget(
        tx_power_dbm=args.tx_power_dbm,
        tx_antenna_gain_dbi=args.tx_gain_dbi,
        rx_antenna_gain_dbi=args.rx_gain_dbi,
        path_loss_db=args.path_loss_db,
        rx_sensitivity_dbm=args.rx_sensitivity_dbm,
        tx_cable_loss_db=args.tx_cable_loss_db,
        rx_cable_loss_db=args.rx_cable_loss_db,
        other_losses_db=args.other_losses_db,
    )
    print(f"EIRP: {result.eirp_dbm:.2f} dBm")
    print(f"Received power: {result.received_power_dbm:.2f} dBm")
    print(f"Fade margin: {result.fade_margin_db:.2f} dB")
    print(f"Link closed: {result.link_closed}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rflinkplanner",
        description="RF link-budget and Fresnel-zone clearance planning toolkit.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("fspl", help="Free-space path loss")
    p.add_argument("--distance-km", type=float, required=True)
    p.add_argument("--freq-mhz", type=float, required=True)
    p.set_defaults(func=_cmd_fspl)

    p = sub.add_parser("hata", help="Okumura-Hata path loss")
    p.add_argument("--freq-mhz", type=float, required=True)
    p.add_argument("--distance-km", type=float, required=True)
    p.add_argument("--tx-height-m", type=float, required=True)
    p.add_argument("--rx-height-m", type=float, required=True)
    p.add_argument(
        "--environment", choices=["urban", "suburban", "open"], default="urban"
    )
    p.add_argument(
        "--city-size", choices=["medium_small", "large"], default="medium_small"
    )
    p.set_defaults(func=_cmd_hata)

    p = sub.add_parser("cost231", help="COST-231 Hata path loss")
    p.add_argument("--freq-mhz", type=float, required=True)
    p.add_argument("--distance-km", type=float, required=True)
    p.add_argument("--tx-height-m", type=float, required=True)
    p.add_argument("--rx-height-m", type=float, required=True)
    p.add_argument("--city-size", choices=["medium", "large"], default="medium")
    p.set_defaults(func=_cmd_cost231)

    p = sub.add_parser("fresnel", help="Fresnel zone radius at a point")
    p.add_argument("--d1-km", type=float, required=True)
    p.add_argument("--d2-km", type=float, required=True)
    p.add_argument("--freq-ghz", type=float, required=True)
    p.add_argument("--zone", type=int, default=1)
    p.set_defaults(func=_cmd_fresnel)

    p = sub.add_parser("linkbudget", help="Full link-budget calculation")
    p.add_argument("--tx-power-dbm", type=float, required=True)
    p.add_argument("--tx-gain-dbi", type=float, required=True)
    p.add_argument("--rx-gain-dbi", type=float, required=True)
    p.add_argument("--path-loss-db", type=float, required=True)
    p.add_argument("--rx-sensitivity-dbm", type=float, required=True)
    p.add_argument("--tx-cable-loss-db", type=float, default=0.0)
    p.add_argument("--rx-cable-loss-db", type=float, default=0.0)
    p.add_argument("--other-losses-db", type=float, default=0.0)
    p.set_defaults(func=_cmd_linkbudget)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
