"""D9 (navamsa) chart: each 30-degree sign split into 9 parts of 3deg20'.

navamsa_sign_index = (sign_index * 9 + part_index) % 12 is the standard
closed-form equivalent of the classical "movable signs count from
themselves, fixed signs count from the 9th sign, dual signs count from the
5th sign" rule.
"""

from app.astro.signs import SIGNS, degree_in_sign, sign_index

_NAVAMSA_SPAN_DEG = 30.0 / 9.0  # 3deg20'


def navamsa_sign_index(sidereal_longitude_deg: float) -> int:
    rashi_index = sign_index(sidereal_longitude_deg)
    part_index = int(degree_in_sign(sidereal_longitude_deg) // _NAVAMSA_SPAN_DEG)
    return (rashi_index * 9 + part_index) % 12


def navamsa_sign_name(sidereal_longitude_deg: float) -> str:
    return SIGNS[navamsa_sign_index(sidereal_longitude_deg)]
