# Contributing to rflinkplanner

Contributions are welcome, particularly:

- Additional propagation models (ITU-R P.1546, Egli, longley-Rice) with a
  cited primary source for the formula used.
- Rain-attenuation / availability models (ITU-R P.530, P.837).
- Real terrain-profile ingestion (SRTM / DEM readers) to feed
  `clearance_profile`.
- Bug reports with a minimal reproducing example.

## Development setup

```bash
git clone https://github.com/MarcoAurelioVieiraMejia/rflinkplanner.git
cd rflinkplanner
pip install -e ".[dev]"
pytest
```

## Guidelines

- Every propagation or clearance formula must cite its source (paper,
  standard, or textbook) in the docstring.
- New public functions need unit tests: at least one hand-derivable
  numeric check and one property-based check (monotonicity, ordering,
  or boundary validation).
- Keep the public API in `rflinkplanner/__init__.py` in sync with any
  new module-level functions you add.
