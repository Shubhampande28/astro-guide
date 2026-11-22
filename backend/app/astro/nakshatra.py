"""Nakshatra (lunar mansion) and pada lookup.

27 nakshatras of 13deg20' (800') each, split into 4 padas of 3deg20' (200').
"""

NAKSHATRAS = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

NAKSHATRA_SPAN_DEG = 360.0 / 27  # 13deg20'
PADA_SPAN_DEG = NAKSHATRA_SPAN_DEG / 4  # 3deg20'


def nakshatra_index(sidereal_longitude_deg: float) -> int:
    """0 = Ashwini, ... 26 = Revati."""
    return int(sidereal_longitude_deg % 360.0 // NAKSHATRA_SPAN_DEG)


def nakshatra_name(sidereal_longitude_deg: float) -> str:
    return NAKSHATRAS[nakshatra_index(sidereal_longitude_deg)]


def pada(sidereal_longitude_deg: float) -> int:
    """1-4, the quarter of the nakshatra the longitude falls in."""
    within_nakshatra = sidereal_longitude_deg % 360.0 % NAKSHATRA_SPAN_DEG
    return int(within_nakshatra // PADA_SPAN_DEG) + 1
