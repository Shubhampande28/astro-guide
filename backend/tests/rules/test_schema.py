import pytest

from app.rules.schema import Rule, RuleEffect, RuleSource


def _base_kwargs(**overrides):
    kwargs = dict(
        id="TEST-1",
        topic="career",
        condition="True == True",
        weight=3,
        effect=RuleEffect(en="x", hi="x", hinglish="x"),
        source=RuleSource(book="Test"),
    )
    kwargs.update(overrides)
    return kwargs


def test_valid_rule_constructs():
    rule = Rule(**_base_kwargs())
    assert rule.status == "draft"


def test_unknown_topic_rejected():
    with pytest.raises(ValueError, match="topic"):
        Rule(**_base_kwargs(topic="astrology"))


def test_weight_out_of_range_rejected():
    with pytest.raises(ValueError, match="weight"):
        Rule(**_base_kwargs(weight=6))
    with pytest.raises(ValueError, match="weight"):
        Rule(**_base_kwargs(weight=-6))


def test_unknown_status_rejected():
    with pytest.raises(ValueError, match="status"):
        Rule(**_base_kwargs(status="published"))
