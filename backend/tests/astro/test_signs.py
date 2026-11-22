from app.astro.signs import degree_in_sign, sign_index, sign_name


def test_sign_index_boundaries() -> None:
    assert sign_index(0.0) == 0  # Aries
    assert sign_index(29.999) == 0
    assert sign_index(30.0) == 1  # Taurus
    assert sign_index(359.999) == 11  # Pisces


def test_sign_index_wraps_above_360() -> None:
    assert sign_index(360.0) == 0
    assert sign_index(395.0) == 1


def test_sign_name() -> None:
    assert sign_name(45.0) == "Taurus"
    assert sign_name(350.0) == "Pisces"


def test_degree_in_sign() -> None:
    assert degree_in_sign(0.0) == 0.0
    assert degree_in_sign(35.0) == 5.0
    assert degree_in_sign(365.0) == 5.0
