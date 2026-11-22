from datetime import UTC, datetime

from app.astro.ayanamsa import lahiri_ayanamsa_degrees
from app.astro.ephemeris import get_timescale


def _ayanamsa_at(year: int) -> float:
    ts = get_timescale()
    t = ts.from_datetime(datetime(year, 1, 1, tzinfo=UTC))
    return lahiri_ayanamsa_degrees(t)


def test_ayanamsa_increases_over_time() -> None:
    # Precession makes the ayanamsa grow by roughly 50 arcsec/year.
    assert _ayanamsa_at(1950) < _ayanamsa_at(2000) < _ayanamsa_at(2026)


def test_ayanamsa_near_published_value_for_2000() -> None:
    # Published Lahiri ayanamsa for 2000-01-01 is ~23.84-23.85 degrees.
    # Within ~5 arcmin, pending calibration against the founder's reference
    # charts (see ayanamsa.py and DECISIONS.md).
    value = _ayanamsa_at(2000)
    assert 23.7 < value < 24.0


def test_ayanamsa_rate_matches_precession() -> None:
    # ~50.29 arcsec/year = ~0.01397 deg/year; over 76 years, ~1.062 degrees.
    delta = _ayanamsa_at(2026) - _ayanamsa_at(1950)
    assert 1.0 < delta < 1.15
