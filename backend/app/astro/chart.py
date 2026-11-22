"""Orchestrates the full Kundli: grahas, lagna, D9, Vimshottari dasha."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time

from app.astro.ascendant import ascendant_tropical_longitude_deg
from app.astro.ayanamsa import lahiri_ayanamsa_degrees
from app.astro.bodies import GRAHAS, compute_positions
from app.astro.dasha import MahaDasha, compute_vimshottari, current_maha_antar
from app.astro.dignity import dignity
from app.astro.ephemeris import get_timescale
from app.astro.houses import house_of
from app.astro.nakshatra import nakshatra_name, pada
from app.astro.navamsa import navamsa_sign_name
from app.astro.signs import degree_in_sign, sign_index, sign_name
from app.astro.time_utils import to_utc


@dataclass
class GrahaResult:
    graha: str
    sidereal_longitude_deg: float
    sign: str
    degree_in_sign: float
    nakshatra: str
    pada: int
    house: int
    dignity: str
    retrograde: bool
    navamsa_sign: str


@dataclass
class LagnaResult:
    sidereal_longitude_deg: float
    sign: str
    degree_in_sign: float
    nakshatra: str
    pada: int


@dataclass
class Chart:
    birth_utc: datetime
    ayanamsa_deg: float
    lagna: LagnaResult
    grahas: list[GrahaResult]
    vimshottari: list[MahaDasha]
    current_maha_dasha: str | None
    current_antar_dasha: str | None


def compute_chart(
    birth_date: date,
    birth_time: time,
    tz_name: str,
    latitude_deg: float,
    longitude_east_deg: float,
    as_of: datetime | None = None,
) -> Chart:
    """Computes the full Kundli for a birth date/time/place.

    `as_of` controls which dasha is reported as "current" (defaults to now);
    pass a fixed value in tests so results are reproducible.
    """
    birth_utc = to_utc(birth_date, birth_time, tz_name)

    ts = get_timescale()
    t = ts.from_datetime(birth_utc)

    ayanamsa = lahiri_ayanamsa_degrees(t)

    tropical_asc = ascendant_tropical_longitude_deg(t, latitude_deg, longitude_east_deg)
    sidereal_asc = (tropical_asc - ayanamsa) % 360.0
    lagna_sign_idx = sign_index(sidereal_asc)

    lagna = LagnaResult(
        sidereal_longitude_deg=sidereal_asc,
        sign=sign_name(sidereal_asc),
        degree_in_sign=degree_in_sign(sidereal_asc),
        nakshatra=nakshatra_name(sidereal_asc),
        pada=pada(sidereal_asc),
    )

    tropical_positions = compute_positions(t, ts)

    grahas = []
    moon_sidereal = 0.0
    for name in GRAHAS:
        tropical_lon = tropical_positions[name].tropical_longitude_deg
        sidereal_lon = (tropical_lon - ayanamsa) % 360.0
        if name == "Moon":
            moon_sidereal = sidereal_lon

        grahas.append(
            GrahaResult(
                graha=name,
                sidereal_longitude_deg=sidereal_lon,
                sign=sign_name(sidereal_lon),
                degree_in_sign=degree_in_sign(sidereal_lon),
                nakshatra=nakshatra_name(sidereal_lon),
                pada=pada(sidereal_lon),
                house=house_of(sidereal_lon, lagna_sign_idx),
                dignity=dignity(name, sidereal_lon),
                retrograde=tropical_positions[name].is_retrograde,
                navamsa_sign=navamsa_sign_name(sidereal_lon),
            )
        )

    vimshottari = compute_vimshottari(moon_sidereal, birth_utc)
    as_of = as_of or datetime.now(UTC)
    current_maha, current_antar = current_maha_antar(vimshottari, as_of)

    return Chart(
        birth_utc=birth_utc,
        ayanamsa_deg=ayanamsa,
        lagna=lagna,
        grahas=grahas,
        vimshottari=vimshottari,
        current_maha_dasha=current_maha,
        current_antar_dasha=current_antar,
    )
