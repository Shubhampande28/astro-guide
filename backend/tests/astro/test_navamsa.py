from app.astro.navamsa import navamsa_sign_index, navamsa_sign_name


def test_aries_navamsa_starts_from_aries() -> None:
    # Movable sign: navamsa counting starts from the sign itself.
    assert navamsa_sign_name(0.0) == "Aries"  # 0deg Aries, part 0
    assert navamsa_sign_name(3.5) == "Taurus"  # part 1


def test_taurus_navamsa_starts_from_capricorn() -> None:
    # Fixed sign: navamsa counting starts from the 9th sign from itself.
    assert navamsa_sign_name(30.0) == "Capricorn"  # 0deg Taurus, part 0


def test_gemini_navamsa_starts_from_libra() -> None:
    # Dual sign: navamsa counting starts from the 5th sign from itself.
    assert navamsa_sign_name(60.0) == "Libra"  # 0deg Gemini, part 0


def test_navamsa_index_wraps_within_12() -> None:
    for lon in range(0, 360, 7):
        assert 0 <= navamsa_sign_index(float(lon)) <= 11
