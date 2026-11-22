from app.astro.houses import house_of, lord_of_house, sign_in_house


def test_house_of_same_sign_as_lagna_is_first_house() -> None:
    lagna_sign_idx = 0  # Aries rising
    assert house_of(sidereal_longitude_deg=15.0, lagna_sign_idx=lagna_sign_idx) == 1


def test_house_of_tenth_house() -> None:
    lagna_sign_idx = 0  # Aries rising -> 10th house is Capricorn (idx 9)
    assert house_of(sidereal_longitude_deg=9 * 30 + 5, lagna_sign_idx=lagna_sign_idx) == 10


def test_sign_in_house_wraps() -> None:
    lagna_sign_idx = 10  # Aquarius rising
    assert sign_in_house(1, lagna_sign_idx) == "Aquarius"
    assert sign_in_house(3, lagna_sign_idx) == "Aries"  # wraps past Pisces


def test_lord_of_house() -> None:
    lagna_sign_idx = 0  # Aries rising
    assert lord_of_house(1, lagna_sign_idx) == "Mars"  # Aries
    assert lord_of_house(10, lagna_sign_idx) == "Saturn"  # Capricorn
