"""ChartContext: the data a rule condition is evaluated against.

Wraps a natal Chart (app.astro.chart.Chart), an optional transit Chart for
`transit(X).house` conditions, and exposes the primitives named in
CLAUDE.md 5.2: lord(n), house(n), planet(X).sign/.dignity/.retro,
aspects(X, n), conj(X, Y), dasha.maha, dasha.antar, transit(X).house.
"""

from dataclasses import dataclass

from app.astro.chart import Chart
from app.astro.houses import lord_of_house
from app.astro.signs import sign_index

# Graha drishti (aspect): every planet aspects the 7th house from itself.
# Mars, Jupiter, and Saturn have additional special aspects (Parashari).
# Rahu/Ketu get only the standard 7th aspect -- classical texts disagree on
# whether they get special aspects too, so this takes the conservative
# reading rather than guessing (see DECISIONS.md).
_ASPECT_OFFSETS = {
    "Mars": (3, 6, 7),
    "Jupiter": (4, 6, 8),
    "Saturn": (2, 6, 9),
}
_DEFAULT_ASPECT_OFFSETS = (6,)


class RuleContextError(Exception):
    """Raised when a rule condition references data this context lacks."""


@dataclass
class ChartContext:
    chart: Chart
    transit_chart: Chart | None = None

    def _graha(self, planet: str):
        for g in self.chart.grahas:
            if g.graha == planet:
                return g
        raise RuleContextError(f"Unknown graha: {planet}")

    def lord_of(self, house_num: int) -> str:
        lagna_idx = sign_index(self.chart.lagna.sidereal_longitude_deg)
        return lord_of_house(house_num, lagna_idx)

    def house_of(self, planet: str) -> int:
        return self._graha(planet).house

    def sign_of(self, planet: str) -> str:
        return self._graha(planet).sign

    def dignity_of(self, planet: str) -> str:
        return self._graha(planet).dignity

    def is_retrograde(self, planet: str) -> bool:
        return self._graha(planet).retrograde

    def nakshatra_of(self, planet: str) -> str:
        return self._graha(planet).nakshatra

    def navamsa_sign_of(self, planet: str) -> str:
        return self._graha(planet).navamsa_sign

    def aspects(self, planet: str, target_house: int) -> bool:
        own_house = self.house_of(planet)
        offsets = _ASPECT_OFFSETS.get(planet, _DEFAULT_ASPECT_OFFSETS)
        aspected = {(own_house - 1 + offset) % 12 + 1 for offset in offsets}
        return target_house in aspected

    def conjunct(self, planet_a: str, planet_b: str) -> bool:
        return self.sign_of(planet_a) == self.sign_of(planet_b)

    @property
    def dasha_maha(self) -> str | None:
        return self.chart.current_maha_dasha

    @property
    def dasha_antar(self) -> str | None:
        return self.chart.current_antar_dasha

    def transit_house_of(self, planet: str) -> int:
        if self.transit_chart is None:
            raise RuleContextError("No transit chart provided for transit() condition")
        lagna_idx = sign_index(self.chart.lagna.sidereal_longitude_deg)
        for g in self.transit_chart.grahas:
            if g.graha == planet:
                transit_sign_idx = sign_index(g.sidereal_longitude_deg)
                return (transit_sign_idx - lagna_idx) % 12 + 1
        raise RuleContextError(f"Unknown graha in transit chart: {planet}")
