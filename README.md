<div align="center">

# rflinkplanner

**Open-source RF link-budget and Fresnel-zone clearance planning toolkit**

*Planning point-to-point wireless links for rural and underserved-area connectivity*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22861090.svg)](https://doi.org/10.5281/zenodo.22861090)
[![tests](https://github.com/MarcoAurelioVieiraMejia/rflinkplanner/actions/workflows/tests.yml/badge.svg)](https://github.com/MarcoAurelioVieiraMejia/rflinkplanner/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)

</div>

---

## Statement of need

Point-to-point wireless links are the backbone of rural connectivity, SCADA
telemetry for utility networks, and telecom backhaul in terrain that fiber
cannot economically reach. Designing one correctly requires three
calculations working together: a **propagation model** to estimate path
loss, a **Fresnel-zone / earth-curvature clearance check** against the real
terrain profile, and a **link budget** that ties transmitter power,
antenna gains, cable losses and receiver sensitivity into a pass/fail
fade margin.

Commercial tools that do this well (Pathloss, Atoll, Ubiquiti LinkPlanner)
are closed-source or vendor-locked; existing open alternatives are either
abandoned, GUI-only, or don't expose a clean, testable API. **rflinkplanner**
provides these three building blocks as a small, dependency-light Python
library with a documented, unit-tested, citable implementation — usable
directly from Python, from the command line, or as a component inside a
larger GIS/planning pipeline.

## Features

- **Propagation models** — free-space path loss, log-distance model,
  Okumura-Hata, and the COST-231 Hata extension (1.5–2 GHz), each with a
  cited primary source and validated input ranges.
- **Fresnel-zone clearance** — first-Fresnel-zone radius, earth-curvature
  bulge (effective-earth-radius model), and a full line-of-sight clearance
  check across an arbitrary terrain profile.
- **Link budget** — EIRP, received power and fade margin from transmitter
  power, antenna gains, feeder losses and receiver sensitivity.
- A small **CLI** (`rflinkplanner`) for quick calculations without writing
  a script.
- Fully unit-tested (`pytest`), with both hand-derived numeric checks and
  property-based checks (monotonicity, environment ordering, input
  validation).

## Installation

```bash
git clone https://github.com/MarcoAurelioVieiraMejia/rflinkplanner.git
cd rflinkplanner
pip install -e .
```

Requires Python ≥ 3.9. The only runtime dependency is `numpy`.

## Quick start

```python
from rflinkplanner import (
    log_distance_path_loss,
    clearance_profile,
    compute_link_budget,
)

# 1. Estimate path loss for a 12 km, 5.8 GHz hop
path_loss_db = log_distance_path_loss(12.0, freq_mhz=5800, path_loss_exponent=2.2)

# 2. Check Fresnel-zone clearance against a terrain profile
profile = clearance_profile(
    terrain_profile=[(0, 1200), (6, 1260), (12, 1180)],  # (km, m elevation)
    tx_height_m=15, rx_height_m=12, freq_ghz=5.8,
)
assert not any(p["obstructed"] for p in profile)

# 3. Close the link budget
budget = compute_link_budget(
    tx_power_dbm=23, tx_antenna_gain_dbi=24, rx_antenna_gain_dbi=24,
    path_loss_db=path_loss_db, rx_sensitivity_dbm=-88,
    tx_cable_loss_db=1.5, rx_cable_loss_db=1.5,
)
print(budget.fade_margin_db, budget.link_closed)
```

See [`examples/rural_link_example.py`](examples/rural_link_example.py) for a
complete worked example from path loss through to the final budget.

### Command line

```bash
rflinkplanner fspl --distance-km 1 --freq-mhz 900
rflinkplanner hata --freq-mhz 900 --distance-km 10 --tx-height-m 50 --rx-height-m 1.5
rflinkplanner fresnel --d1-km 5 --d2-km 5 --freq-ghz 2.4
rflinkplanner linkbudget --tx-power-dbm 20 --tx-gain-dbi 24 --rx-gain-dbi 24 \
    --path-loss-db 130 --rx-sensitivity-dbm -85
```

## Roadmap

- ITU-R P.1546 and Longley-Rice propagation models.
- Rain-attenuation / link-availability estimation (ITU-R P.530, P.837).
- Native ingestion of digital elevation models (SRTM/DEM) into
  `clearance_profile`, instead of manually supplied terrain samples.

Contributions on any of the above are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Citation

This software is archived on Zenodo with a citable DOI. If it is useful in
your work, please cite it:

> Vieira Mejía, M. A. (2026). *rflinkplanner: An open-source toolkit for
> RF link-budget and Fresnel-zone clearance planning* (v0.1.0). Zenodo.
> https://doi.org/10.5281/zenodo.22861090

BibTeX:

```bibtex
@software{vieiramejia_rflinkplanner_2026,
  author    = {Vieira Mejía, Marco Aurelio},
  title      = {rflinkplanner: An open-source toolkit for RF link-budget
               and Fresnel-zone clearance planning},
  year       = {2026},
  version    = {v0.1.0},
  publisher = {Zenodo},
  doi        = {10.5281/zenodo.22861090},
  url        = {https://doi.org/10.5281/zenodo.22861090}
}
```

Machine-readable metadata is also provided in [`CITATION.cff`](CITATION.cff),
from which GitHub renders a "Cite this repository" button automatically.

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

## About the author

**Marco Aurelio Vieira Mejía**

Ingeniero con 38 años de trayectoria en el sector de infraestructura en
Colombia. Gerente General de **[Ingeomega S.A.S.](https://ingeomega.com.co)**
(Medellín, 1988), empresa con más de 4.000 colaboradores directos y
presencia en más de 20 departamentos del país, con más de 250 proyectos
ejecutados en energía eléctrica, telecomunicaciones, agua potable y
saneamiento, gas combustible y obra civil — entre ellos la línea de
transmisión Chorodó–Caucheras (77 km, 110 kV), el proyecto de generación
solar TERRA y la subestación La Marina en Cartagena.

> *"El activo más sólido de un proyecto no está en los datos, sino en las
> personas."*

**rflinkplanner** es una contribución personal de código abierto a la
comunidad de telecomunicaciones e ingeniería de infraestructura,
construida en el tiempo libre y ofrecida sin garantías comerciales.

[Sitio web](https://marcoaureliovieiramejia.com.co/) ·
[LinkedIn](https://www.linkedin.com/in/marco-aurelio-vieira-mejia-b7a332373) ·
[Ingeomega S.A.S.](https://ingeomega.com.co)

</div>
