import pytest

from app.rules.dsl import DslError, evaluate, parse


def test_planet_dignity(sample_ctx):
    assert evaluate(parse("planet(Venus).dignity == 'exalted'"), sample_ctx) is True
    assert evaluate(parse("planet(Sun).dignity == 'exalted'"), sample_ctx) is False


def test_planet_sign(sample_ctx):
    assert evaluate(parse("planet(Mars).sign == 'Aquarius'"), sample_ctx) is True


def test_planet_retro(sample_ctx):
    assert evaluate(parse("planet(Saturn).retro == True"), sample_ctx) is True
    assert evaluate(parse("planet(Sun).retro == False"), sample_ctx) is True


def test_lord_in_house(sample_ctx):
    # lord(10) = Jupiter (Pisces rules house 10 from Gemini lagna); Jupiter
    # occupies house 1 itself.
    assert evaluate(parse("lord(10) in house(1)"), sample_ctx) is True
    assert evaluate(parse("lord(10) in house(5)"), sample_ctx) is False


def test_conj(sample_ctx):
    assert evaluate(parse("conj(Saturn, Rahu)"), sample_ctx) is True
    assert evaluate(parse("conj(Sun, Moon)"), sample_ctx) is False


def test_aspects(sample_ctx):
    # Saturn is in house 8; its special aspects land on houses 10, 2, 5.
    assert evaluate(parse("aspects(Saturn, 2)"), sample_ctx) is True
    assert evaluate(parse("aspects(Saturn, 3)"), sample_ctx) is False


def test_dasha_attrs(sample_ctx):
    # At birth, the maha/antar dasha lord is the birth nakshatra's lord
    # (Moon in Uttara Ashadha -> Sun); the antar sequence starts from the
    # maha lord itself.
    assert evaluate(parse("dasha.maha == 'Sun'"), sample_ctx) is True
    assert evaluate(parse("dasha.antar == 'Sun'"), sample_ctx) is True
    assert evaluate(parse("dasha.maha == 'Rahu'"), sample_ctx) is False


def test_and_or_not(sample_ctx):
    cond = "planet(Mars).sign == 'Aquarius' and not planet(Mars).retro == True"
    assert evaluate(parse(cond), sample_ctx) is True
    cond2 = "planet(Sun).dignity == 'exalted' or dasha.maha == 'Sun'"
    assert evaluate(parse(cond2), sample_ctx) is True


def test_parentheses(sample_ctx):
    cond = "(planet(Saturn).dignity == 'own') and (dasha.maha == 'Sun')"
    assert evaluate(parse(cond), sample_ctx) is True


@pytest.mark.parametrize(
    "bad_condition",
    [
        "__import__('os').system('ls')",
        "lord(10).__class__",
        "open('x')",
        "1 + 1",
        "lord(10) in [1, 2, 3]",
        "lambda: True",
        "planet(Sun).sign == 'Leo' == planet(Moon).sign == 'Leo'",
    ],
)
def test_rejects_unsafe_or_unsupported_syntax(bad_condition):
    with pytest.raises(DslError):
        parse(bad_condition)


def test_rejects_unknown_planet_name():
    with pytest.raises(DslError):
        parse("planet(Pluto).sign == 'Leo'")
