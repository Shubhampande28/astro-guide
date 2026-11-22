"""Whole-sign houses: house N occupies exactly one sign, counted from the
lagna (ascendant) sign.
"""

from app.astro.signs import SIGNS, sign_index

SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}


def house_of(sidereal_longitude_deg: float, lagna_sign_idx: int) -> int:
    """1-12, the whole-sign house a longitude falls in, relative to lagna."""
    return (sign_index(sidereal_longitude_deg) - lagna_sign_idx) % 12 + 1


def sign_in_house(house_num: int, lagna_sign_idx: int) -> str:
    """Which sign occupies house `house_num` (1-12)."""
    return SIGNS[(lagna_sign_idx + house_num - 1) % 12]


def lord_of_house(house_num: int, lagna_sign_idx: int) -> str:
    """The graha ruling the sign in house `house_num`."""
    return SIGN_LORDS[sign_in_house(house_num, lagna_sign_idx)]
