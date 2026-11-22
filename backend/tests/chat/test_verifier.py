from app.chat.verifier import verify


def test_accepts_clean_text(sample_chart):
    assert verify("Jupiter in the 1st house brings good fortune.", sample_chart) is True


def test_rejects_invalid_body_name(sample_chart):
    assert verify("Pluto in the 10th house affects your career.", sample_chart) is False


def test_rejects_out_of_range_house(sample_chart):
    assert verify("Saturn in the 13th house causes delays.", sample_chart) is False


def test_rejects_unknown_dasha_lord(sample_chart):
    assert verify("The Pluto dasha is currently active.", sample_chart) is False


def test_accepts_known_dasha_lord(sample_chart):
    assert verify("The Jupiter dasha brings growth.", sample_chart) is True
