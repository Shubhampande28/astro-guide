"""Geocentric apparent ecliptic longitude (true equinox of date) for each
graha, plus retrograde detection.

Rahu uses the mean lunar node (Meeus, *Astronomical Algorithms* ch. 47);
Ketu = Rahu + 180 deg exactly, per CLAUDE.md 5.1.
"""

from dataclasses import dataclass

from skyfield.timelib import Time

from app.astro.ephemeris import get_ephemeris

GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

_EPHEMERIS_TARGETS = {
    "Sun": "sun",
    "Moon": "moon",
    "Mars": "mars barycenter",
    "Mercury": "mercury barycenter",
    "Jupiter": "jupiter barycenter",
    "Venus": "venus barycenter",
    "Saturn": "saturn barycenter",
}

# Grahas whose apparent motion is always technically "forward" in Vedic
# astrology convention: the Sun and Moon are never recorded as retrograde,
# and the mean lunar node (Rahu/Ketu) always regresses, so it is always
# retrograde by convention.
_NEVER_RETROGRADE = {"Sun", "Moon"}
_ALWAYS_RETROGRADE = {"Rahu", "Ketu"}

# Small time step used to estimate daily motion for retrograde detection.
_RETRO_STEP_DAYS = 1.0


def tropical_longitude_deg(graha: str, t: Time) -> float:
    """Geocentric apparent tropical ecliptic longitude, true equinox of date."""
    if graha == "Rahu":
        return _mean_node_longitude_deg(t)
    if graha == "Ketu":
        return (_mean_node_longitude_deg(t) + 180.0) % 360.0

    eph = get_ephemeris()
    earth = eph["earth"]
    target = eph[_EPHEMERIS_TARGETS[graha]]
    apparent = earth.at(t).observe(target).apparent()
    _, lon, _ = apparent.ecliptic_latlon(epoch="date")
    return lon.degrees % 360.0


def _mean_node_longitude_deg(t: Time) -> float:
    """Meeus (1998) ch. 47, mean longitude of the ascending lunar node."""
    jd_tt = t.tt
    t_centuries = (jd_tt - 2451545.0) / 36525.0
    omega = (
        125.0445479
        - 1934.1362891 * t_centuries
        + 0.0020754 * t_centuries**2
        + t_centuries**3 / 467441.0
        - t_centuries**4 / 60616000.0
    )
    return omega % 360.0


@dataclass
class GrahaPosition:
    graha: str
    tropical_longitude_deg: float
    is_retrograde: bool


def compute_positions(t: Time, ts) -> dict[str, GrahaPosition]:
    """All 9 grahas' tropical longitude + retrograde flag at time `t`."""
    t_next = ts.tt_jd(t.tt + _RETRO_STEP_DAYS)
    positions: dict[str, GrahaPosition] = {}
    for graha in GRAHAS:
        lon = tropical_longitude_deg(graha, t)
        if graha in _NEVER_RETROGRADE:
            retro = False
        elif graha in _ALWAYS_RETROGRADE:
            retro = True
        else:
            lon_next = tropical_longitude_deg(graha, t_next)
            delta = (lon_next - lon + 540.0) % 360.0 - 180.0  # signed, wrap-safe
            retro = bool(delta < 0)  # longitudes can be numpy floats; keep this a plain bool
        positions[graha] = GrahaPosition(graha, lon, retro)
    return positions
