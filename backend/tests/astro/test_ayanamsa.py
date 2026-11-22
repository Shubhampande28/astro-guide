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


def test_ayanamsa_matches_swiss_ephemeris_lahiri() -> None:
    # Cross-checked against Swiss Ephemeris's SIDM_LAHIRI mode (used only as
    # a local, throwaway verification oracle, never a product dependency --
    # see ayanamsa.py and DECISIONS.md) across 1900-2100; matched to better
    # than 0.01 arcsec. These are fixed expected values from that check.
    expected = {
        1900: 22.460531,
        1943: 23.060956,
        2000: 23.857073,
        2026: 24.220304,
        2100: 25.254268,
    }
    for year, expected_deg in expected.items():
        assert abs(_ayanamsa_at(year) - expected_deg) < 0.0001


def test_ayanamsa_rate_matches_precession() -> None:
    # ~50.29 arcsec/year = ~0.01397 deg/year; over 76 years, ~1.062 degrees.
    delta = _ayanamsa_at(2026) - _ayanamsa_at(1950)
    assert 1.0 < delta < 1.15
