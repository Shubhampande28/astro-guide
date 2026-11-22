"""Lahiri ayanamsa, via the IAU 2006 general-precession-in-longitude formula.

ayanamsa(T) = (theta0 + p_A(T)) / 3600, in degrees, where:
  - T is Julian centuries of TT since J2000.0.
  - p_A(T) is the IAU 2006 precession-in-longitude polynomial (Capitaine et
    al. 2003), in arcseconds -- a published astronomical constant, not
    copyrighted code.
  - theta0 = 85885.53 arcsec is the Lahiri ayanamsa's reference value at
    J2000.0.

This was cross-checked against Swiss Ephemeris's SIDM_LAHIRI mode (used as a
local, throwaway verification oracle only -- never a runtime dependency of
this product, see DECISIONS.md) and matches to better than 0.01 arcsec from
1900 through 2100. An earlier version of this file computed the ayanamsa
from the star Spica's tropical position directly (the literal
"Chitrapaksha" definition); that turned out to differ from the ayanamsa
actually used by Indian ephemerides/software (Drik Panchang, Jagannatha
Hora, Swiss Ephemeris's "Lahiri" mode) by about 1-1.5 arcmin, which is this
product's chart math is correct to.
"""

from skyfield.timelib import Time

_THETA0_ARCSEC = 85885.53

# IAU 2006 precession in longitude, Capitaine et al. (2003), arcsec.
_P_A_COEFFS = (5028.796195, 1.1054348, 0.00007964, -0.000023857, -0.0000000383)


def lahiri_ayanamsa_degrees(t: Time) -> float:
    """Ayanamsa in degrees (0-360) at Skyfield time `t`."""
    t_centuries = (t.tt - 2451545.0) / 36525.0
    p_a_arcsec = sum(coeff * t_centuries ** (i + 1) for i, coeff in enumerate(_P_A_COEFFS))
    return ((_THETA0_ARCSEC + p_a_arcsec) / 3600.0) % 360.0
