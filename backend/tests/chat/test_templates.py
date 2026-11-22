from app.chat.templates import build_clarifying_question, build_declined, build_topic_answer
from app.rules.evaluator import evaluate_topic
from app.rules.schema import Rule, RuleEffect, RuleSource


def _rule(id_, condition, weight, book="Test"):
    return Rule(
        id=id_,
        topic="career",
        condition=condition,
        weight=weight,
        effect=RuleEffect(en=f"en-{id_}", hi=f"hi-{id_}", hinglish=f"hing-{id_}"),
        source=RuleSource(book=book),
        status="approved",
    )


def test_build_topic_answer_with_matches(sample_chart, sample_ctx):
    rules = [_rule("A", "planet(Venus).dignity == 'exalted'", 4)]
    report = evaluate_topic("career", rules, sample_chart, sample_ctx)
    card = build_topic_answer("career", report, "en")
    assert card.topic == "career"
    assert "career" in card.summary.lower()
    assert card.why == ["en-A"]
    assert card.sources == ["Test"]
    assert card.confidence in ("medium", "high")
    assert card.is_declined is False
    assert card.is_clarifying_question is False


def test_build_topic_answer_language_selection(sample_chart, sample_ctx):
    rules = [_rule("A", "planet(Venus).dignity == 'exalted'", 4)]
    report = evaluate_topic("career", rules, sample_chart, sample_ctx)
    card_hi = build_topic_answer("career", report, "hi")
    assert card_hi.why == ["hi-A"]
    card_hing = build_topic_answer("career", report, "hinglish")
    assert card_hing.why == ["hing-A"]


def test_build_topic_answer_no_matches_is_low_confidence(sample_chart, sample_ctx):
    rules = [_rule("A", "planet(Sun).dignity == 'exalted'", 4)]  # false for this chart
    report = evaluate_topic("career", rules, sample_chart, sample_ctx)
    card = build_topic_answer("career", report, "en")
    assert card.confidence == "low"
    assert card.why == []


def test_build_declined_has_no_rules_content():
    card = build_declined("death", "en")
    assert card.is_declined is True
    assert card.why == []
    assert card.topic == "death"


def test_build_clarifying_question():
    card = build_clarifying_question("hi")
    assert card.is_clarifying_question is True
    assert card.topic is None
