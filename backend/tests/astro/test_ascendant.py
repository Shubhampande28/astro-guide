from datetime import UTC, datetime

from app.astro.ascendant import (
    ascendant_tropical_longitude_deg,
    local_sidereal_time_deg,
    mean_obliquity_deg,
)
from app.astro.ephemeris import get_timescale


def test_mean_obliquity_near_j2000_value() -> None:
    ts = get_timescale()
    t = ts.from_datetime(datetime(2000, 1, 1, 12, tzinfo=UTC))
    # IAU 2006 value at J2000.0 is 23 deg 26' 21.406" = 23.4392794 deg.
    assert abs(mean_obliquity_deg(t) - 23.4392794) < 0.0001


def test_local_sidereal_time_in_range() -> None:
    ts = get_timescale()
    t = ts.from_datetime(datetime(2000, 1, 1, 12, tzinfo=UTC))
    for lon in (-180, -77.0, 0.0, 77.2, 180):
        lst = local_sidereal_time_deg(t, lon)
        assert 0.0 <= lst < 360.0


def test_ascendant_in_valid_range() -> None:
    ts = get_timescale()
    t = ts.from_datetime(datetime(2000, 1, 1, 12, tzinfo=UTC))
    # New Delhi
    asc = ascendant_tropical_longitude_deg(t, latitude_deg=28.6139, longitude_east_deg=77.2090)
    assert 0.0 <= asc < 360.0


def test_ascendant_changes_over_a_day() -> None:
    ts = get_timescale()
    t1 = ts.from_datetime(datetime(2000, 1, 1, 6, tzinfo=UTC))
    t2 = ts.from_datetime(datetime(2000, 1, 1, 18, tzinfo=UTC))
    asc1 = ascendant_tropical_longitude_deg(t1, 28.6139, 77.2090)
    asc2 = ascendant_tropical_longitude_deg(t2, 28.6139, 77.2090)
    assert asc1 != asc2
