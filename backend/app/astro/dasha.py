"""Vimshottari dasha: maha dasha (9 periods, 120-year cycle) and antar dasha.

Dasha year = 365.25 days, per CLAUDE.md 5.1.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.astro.nakshatra import NAKSHATRA_SPAN_DEG, nakshatra_index

DASHA_YEAR_DAYS = 365.25

# Fixed order and duration (years) of the 9 Vimshottari lords; sums to 120.
_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

# 27 nakshatra lords: the 9-lord sequence repeated 3 times.
_NAKSHATRA_LORDS = _SEQUENCE * 3


@dataclass
class AntarDasha:
    lord: str
    start: datetime
    end: datetime


@dataclass
class MahaDasha:
    lord: str
    start: datetime
    end: datetime
    antar_dashas: list[AntarDasha]


def _antar_dashas(maha_lord: str, start: datetime, maha_years: float) -> list[AntarDasha]:
    """Antar dasha order starts from the maha lord itself, then continues
    the fixed sequence; each sub-period is maha_years * (sub_lord_years/120).
    """
    start_idx = _SEQUENCE.index(maha_lord)
    order = _SEQUENCE[start_idx:] + _SEQUENCE[:start_idx]

    periods = []
    cursor = start
    for lord in order:
        duration_days = maha_years * (_YEARS[lord] / 120.0) * DASHA_YEAR_DAYS
        end = cursor + timedelta(days=duration_days)
        periods.append(AntarDasha(lord, cursor, end))
        cursor = end
    return periods


def compute_vimshottari(moon_sidereal_longitude_deg: float, birth_utc: datetime) -> list[MahaDasha]:
    """Full 120-year Vimshottari timeline (9 maha dashas) from birth."""
    nak_idx = nakshatra_index(moon_sidereal_longitude_deg)
    birth_lord = _NAKSHATRA_LORDS[nak_idx]

    position_in_nakshatra = moon_sidereal_longitude_deg % 360.0 % NAKSHATRA_SPAN_DEG
    elapsed_fraction = position_in_nakshatra / NAKSHATRA_SPAN_DEG

    start_idx = _SEQUENCE.index(birth_lord)
    order = _SEQUENCE[start_idx:] + _SEQUENCE[:start_idx]

    maha_dashas = []
    cursor = birth_utc
    for i, lord in enumerate(order):
        full_years = _YEARS[lord]
        years_remaining = full_years * (1 - elapsed_fraction) if i == 0 else full_years
        duration_days = years_remaining * DASHA_YEAR_DAYS
        end = cursor + timedelta(days=duration_days)
        antar_dashas = _antar_dashas(lord, cursor, years_remaining)
        maha_dashas.append(MahaDasha(lord, cursor, end, antar_dashas))
        cursor = end

    return maha_dashas


def current_maha_antar(maha_dashas: list[MahaDasha], at: datetime) -> tuple[str | None, str | None]:
    """The maha/antar dasha lords active at datetime `at`, or (None, None)."""
    for maha in maha_dashas:
        if maha.start <= at < maha.end:
            for antar in maha.antar_dashas:
                if antar.start <= at < antar.end:
                    return maha.lord, antar.lord
            return maha.lord, None
    return None, None
