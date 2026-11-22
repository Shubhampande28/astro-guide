from app.astro.nakshatra import nakshatra_index, nakshatra_name, pada


def test_nakshatra_index_boundaries() -> None:
    assert nakshatra_index(0.0) == 0  # Ashwini
    assert nakshatra_index(13.0) == 0
    assert nakshatra_index(13.34) == 1  # Bharani
    assert nakshatra_index(359.99) == 26  # Revati


def test_nakshatra_name() -> None:
    assert nakshatra_name(0.0) == "Ashwini"
    assert nakshatra_name(356.0) == "Revati"


def test_pada_boundaries() -> None:
    assert pada(0.0) == 1
    assert pada(3.3) == 1
    assert pada(3.4) == 2
    assert pada(6.9) == 3
    assert pada(13.3) == 4
