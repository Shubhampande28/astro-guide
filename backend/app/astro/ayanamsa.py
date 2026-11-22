"""Lahiri (Chitrapaksha) ayanamsa.

Defined as: tropical ecliptic longitude of Spica (Chitra) minus 180 degrees.
This is the literal "Chitrapaksha" definition CLAUDE.md names (Spica anchors
the zero point of the sidereal zodiac). Spica's position is computed with
full precession + nutation + aberration via Skyfield, so the ayanamsa value
already changes correctly year to year.

CALIBRATION_OFFSET_DEG exists because published Lahiri tables (Indian
Astronomical Ephemeris) differ by a few arcseconds to roughly half an
arcminute from a pure Spica-at-180-degrees calculation, depending on exactly
which historical Spica coordinates and precession model were used when the
committee fixed the official value. Phase 1's accuracy gate (10 reference
charts from the founder) is what calibrates this constant; it defaults to 0.
See DECISIONS.md.
"""

from skyfield.api import Star
from skyfield.timelib import Time

from app.astro.ephemeris import get_ephemeris

CALIBRATION_OFFSET_DEG = 0.0

# Spica (Alpha Virginis), ICRS J2000 coordinates.
_SPICA = Star(ra_hours=(13, 25, 11.579), dec_degrees=(-11, 9, 40.75))


def lahiri_ayanamsa_degrees(t: Time) -> float:
    """Ayanamsa in degrees (0-360) at Skyfield time `t`."""
    eph = get_ephemeris()
    earth = eph["earth"]
    apparent = earth.at(t).observe(_SPICA).apparent()
    _, lon, _ = apparent.ecliptic_latlon(epoch="date")
    ayanamsa = (lon.degrees - 180.0 + CALIBRATION_OFFSET_DEG) % 360.0
    return ayanamsa
