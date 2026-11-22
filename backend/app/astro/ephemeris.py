"""Loads the NASA JPL DE440s ephemeris (MIT-compatible, public domain) via Skyfield.

The .bsp file (~32MB) is downloaded on first use into backend/data/, which is
gitignored, rather than committed to the repo.
"""

from functools import lru_cache
from pathlib import Path

from skyfield.api import Loader
from skyfield.jpllib import SpiceKernel
from skyfield.timelib import Timescale

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@lru_cache
def get_loader() -> Loader:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return Loader(str(DATA_DIR))


@lru_cache
def get_ephemeris() -> SpiceKernel:
    return get_loader()("de440s.bsp")


@lru_cache
def get_timescale() -> Timescale:
    return get_loader().timescale()
