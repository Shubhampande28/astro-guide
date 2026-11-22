from datetime import UTC, datetime, timedelta

from app.astro.dasha import compute_vimshottari, current_maha_antar


def test_total_cycle_is_120_years() -> None:
    birth = datetime(2000, 1, 1, tzinfo=UTC)
    dashas = compute_vimshottari(moon_sidereal_longitude_deg=0.0, birth_utc=birth)
    total_days = (dashas[-1].end - dashas[0].start).days
    # 120 years at 365.25 days/year, balance already accounted for.
    assert abs(total_days - 120 * 365.25) < 2


def test_nine_maha_dashas_in_order_from_birth_lord() -> None:
    # 0 degrees sidereal longitude = Ashwini, ruled by Ketu.
    birth = datetime(2000, 1, 1, tzinfo=UTC)
    dashas = compute_vimshottari(moon_sidereal_longitude_deg=0.0, birth_utc=birth)
    lords = [d.lord for d in dashas]
    assert lords == ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]


def test_antar_dashas_sum_to_maha_duration() -> None:
    birth = datetime(2000, 1, 1, tzinfo=UTC)
    dashas = compute_vimshottari(moon_sidereal_longitude_deg=0.0, birth_utc=birth)
    for maha in dashas:
        assert maha.antar_dashas[0].start == maha.start
        assert maha.antar_dashas[-1].end == maha.end
        for a, b in zip(maha.antar_dashas, maha.antar_dashas[1:], strict=False):
            assert a.end == b.start


def test_balance_at_birth_shortens_first_maha_dasha() -> None:
    birth = datetime(2000, 1, 1, tzinfo=UTC)
    # Exactly halfway through Ashwini (Ketu, 7 years) -> ~3.5 years remaining.
    halfway = 360.0 / 27 / 2
    dashas = compute_vimshottari(moon_sidereal_longitude_deg=halfway, birth_utc=birth)
    first_years = (dashas[0].end - dashas[0].start).days / 365.25
    assert abs(first_years - 3.5) < 0.05


def test_current_maha_antar_lookup() -> None:
    birth = datetime(2000, 1, 1, tzinfo=UTC)
    dashas = compute_vimshottari(moon_sidereal_longitude_deg=0.0, birth_utc=birth)
    maha, antar = current_maha_antar(dashas, birth + timedelta(days=1))
    assert maha == "Ketu"
    assert antar == "Ketu"  # antar dasha order starts from the maha lord itself


def test_current_maha_antar_none_outside_range() -> None:
    birth = datetime(2000, 1, 1, tzinfo=UTC)
    dashas = compute_vimshottari(moon_sidereal_longitude_deg=0.0, birth_utc=birth)
    maha, antar = current_maha_antar(dashas, birth - timedelta(days=1))
    assert maha is None
    assert antar is None
