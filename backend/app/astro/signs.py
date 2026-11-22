"""Zodiac sign lookup, shared by rashi (D1) and navamsa (D9) calculations."""

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def sign_index(sidereal_longitude_deg: float) -> int:
    """0 = Aries, 1 = Taurus, ... 11 = Pisces."""
    return int(sidereal_longitude_deg % 360.0 // 30)


def sign_name(sidereal_longitude_deg: float) -> str:
    return SIGNS[sign_index(sidereal_longitude_deg)]


def degree_in_sign(sidereal_longitude_deg: float) -> float:
    """0-30, the planet's position within its own sign."""
    return sidereal_longitude_deg % 30.0
