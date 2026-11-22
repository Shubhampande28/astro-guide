import pytest

from app.rules.context import ChartContext, RuleContextError


def test_lord_of(sample_ctx):
    assert sample_ctx.lord_of(10) == "Jupiter"
    assert sample_ctx.lord_of(1) == "Mercury"  # Gemini lagna


def test_house_of(sample_ctx):
    assert sample_ctx.house_of("Jupiter") == 1
    assert sample_ctx.house_of("Venus") == 10


def test_unknown_graha_raises(sample_ctx):
    with pytest.raises(RuleContextError):
        sample_ctx.house_of("Pluto")


def test_transit_without_transit_chart_raises(sample_ctx):
    with pytest.raises(RuleContextError):
        sample_ctx.transit_house_of("Sun")


def test_transit_with_transit_chart(sample_chart):
    ctx = ChartContext(chart=sample_chart, transit_chart=sample_chart)
    # Using the natal chart as its own "transit" chart: every graha should
    # transit the same house it natally occupies.
    assert ctx.transit_house_of("Jupiter") == 1
    assert ctx.transit_house_of("Venus") == 10
