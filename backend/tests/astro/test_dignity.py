from app.astro.dignity import dignity


def test_sun_exalted_in_aries() -> None:
    assert dignity("Sun", 5.0) == "exalted"


def test_sun_debilitated_in_libra() -> None:
    assert dignity("Sun", 185.0) == "debilitated"


def test_sun_own_sign_leo() -> None:
    # Leo 25deg: own sign, but outside the moolatrikona range (0-20deg).
    assert dignity("Sun", 145.0) == "own"


def test_sun_moolatrikona_leo_early_degrees() -> None:
    assert dignity("Sun", 120.0 + 5.0) == "moolatrikona"


def test_neutral_otherwise() -> None:
    assert dignity("Sun", 50.0) == "neutral"  # Taurus


def test_rahu_ketu_have_no_classical_dignity() -> None:
    assert dignity("Rahu", 10.0) == "neutral"
    assert dignity("Ketu", 190.0) == "neutral"
