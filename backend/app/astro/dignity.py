"""Planetary dignity: exalted, debilitated, own sign, moolatrikona, or neutral.

Sign-level dignity for the 7 classical grahas (Sun-Saturn). Rahu/Ketu are
left as "neutral": classical texts disagree on their exaltation signs, so
rather than guess we report no dignity for them (see DECISIONS.md). This can
be revisited once the founder (an astrologer, per CLAUDE.md) picks a
tradition.
"""

from app.astro.signs import degree_in_sign, sign_name

_EXALTATION_SIGN = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mars": "Capricorn",
    "Mercury": "Virgo",
    "Jupiter": "Cancer",
    "Venus": "Pisces",
    "Saturn": "Libra",
}

_DEBILITATION_SIGN = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries",
}

_OWN_SIGNS = {
    "Sun": {"Leo"},
    "Moon": {"Cancer"},
    "Mars": {"Aries", "Scorpio"},
    "Mercury": {"Gemini", "Virgo"},
    "Jupiter": {"Sagittarius", "Pisces"},
    "Venus": {"Taurus", "Libra"},
    "Saturn": {"Capricorn", "Aquarius"},
}

# (sign, low_degree, high_degree) within the sign.
_MOOLATRIKONA = {
    "Sun": ("Leo", 0.0, 20.0),
    "Moon": ("Taurus", 4.0, 30.0),
    "Mars": ("Aries", 0.0, 12.0),
    "Mercury": ("Virgo", 16.0, 20.0),
    "Jupiter": ("Sagittarius", 0.0, 10.0),
    "Venus": ("Libra", 0.0, 15.0),
    "Saturn": ("Aquarius", 0.0, 20.0),
}


def dignity(graha: str, sidereal_longitude_deg: float) -> str:
    """Returns one of: exalted, debilitated, moolatrikona, own, neutral."""
    if graha not in _EXALTATION_SIGN:
        return "neutral"

    sign = sign_name(sidereal_longitude_deg)
    deg_in_sign = degree_in_sign(sidereal_longitude_deg)

    if sign == _EXALTATION_SIGN[graha]:
        return "exalted"
    if sign == _DEBILITATION_SIGN[graha]:
        return "debilitated"

    moola_sign, low, high = _MOOLATRIKONA[graha]
    if sign == moola_sign and low <= deg_in_sign <= high:
        return "moolatrikona"

    if sign in _OWN_SIGNS[graha]:
        return "own"

    return "neutral"
