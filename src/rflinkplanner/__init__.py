"""rflinkplanner: RF link-budget and Fresnel-zone clearance planning toolkit."""

from .propagation import (
    free_space_path_loss,
    log_distance_path_loss,
    okumura_hata,
    cost231_hata,
)
from .fresnel import (
    fresnel_zone_radius,
    earth_curvature_bulge,
    clearance_profile,
)
from .linkbudget import LinkBudgetResult, compute_link_budget

__version__ = "0.1.0"

__all__ = [
    "free_space_path_loss",
    "log_distance_path_loss",
    "okumura_hata",
    "cost231_hata",
    "fresnel_zone_radius",
    "earth_curvature_bulge",
    "clearance_profile",
    "LinkBudgetResult",
    "compute_link_budget",
]
