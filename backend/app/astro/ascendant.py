"""Ascendant (lagna): local sidereal time + obliquity + latitude.

Formula from Meeus, *Astronomical Algorithms* ch. 24: given RAMC (local
apparent sidereal time, in degrees), obliquity of the ecliptic eps, and
geographic latitude phi, the tropical ecliptic longitude of the ascendant
is:

    tan(Asc) = -cos(RAMC) / (sin(eps) * tan(phi) + cos(eps) * sin(RAMC))
"""

import math

from skyfield.timelib import Time


def mean_obliquity_deg(t: Time) -> float:
    """IAU 2006 mean obliquity of the ecliptic, in degrees."""
    t_centuries = (t.tt - 2451545.0) / 36525.0
    arcsec = (
        84381.406
        - 46.836769 * t_centuries
        - 0.0001831 * t_centuries**2
        + 0.00200340 * t_centuries**3
        - 0.576e-6 * t_centuries**4
        - 4.34e-8 * t_centuries**5
    )
    return arcsec / 3600.0


def local_sidereal_time_deg(t: Time, longitude_east_deg: float) -> float:
    """RAMC: local apparent sidereal time, in degrees (0-360)."""
    gast_deg = t.gast * 15.0
    return (gast_deg + longitude_east_deg) % 360.0


def ascendant_tropical_longitude_deg(
    t: Time, latitude_deg: float, longitude_east_deg: float
) -> float:
    ramc = math.radians(local_sidereal_time_deg(t, longitude_east_deg))
    eps = math.radians(mean_obliquity_deg(t))
    phi = math.radians(latitude_deg)

    numerator = -math.cos(ramc)
    denominator = math.sin(eps) * math.tan(phi) + math.cos(eps) * math.sin(ramc)
    asc = math.degrees(math.atan2(numerator, denominator))
    return asc % 360.0
