"""Verifies an AI-rewritten summary before it's shown to the user
(CLAUDE.md 5.3 step 7): every planet, house, and dasha lord mentioned must
exist in the chart. If verification fails, the caller must fall back to
the template text -- this module only answers the yes/no question, it
never edits the text itself.
"""

import re

from app.astro.bodies import GRAHAS
from app.astro.chart import Chart

_VALID_GRAHAS = set(GRAHAS)

# Bodies a language model might plausibly mention that this system never
# uses (CLAUDE.md 5.1 only computes the 9 classical grahas).
_INVALID_BODY_NAMES = {"Pluto", "Uranus", "Neptune", "Ascendant lord", "Chiron"}

_HOUSE_NUMBER_PATTERN = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+house\b", re.IGNORECASE)
_DASHA_PATTERN = re.compile(r"\b([A-Za-z]+)\s+dasha\b", re.IGNORECASE)


def verify(text: str, chart: Chart) -> bool:
    """True if every planet/house/dasha reference in `text` is consistent
    with `chart`; False means the caller must discard this text."""
    for invalid_name in _INVALID_BODY_NAMES:
        if invalid_name.lower() in text.lower():
            return False

    for match in _HOUSE_NUMBER_PATTERN.finditer(text):
        house_num = int(match.group(1))
        if not 1 <= house_num <= 12:
            return False

    for match in _DASHA_PATTERN.finditer(text):
        planet_name = match.group(1)
        if planet_name.capitalize() not in _VALID_GRAHAS:
            return False

    return True
