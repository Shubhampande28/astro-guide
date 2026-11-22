from app.chat.pipeline import handle_message
from app.rules.loader import load_all_rules

RULES = list(load_all_rules())


def test_distress_message_short_circuits_everything(sample_chart):
    card = handle_message("I want to kill myself", sample_chart, RULES)
    assert card.is_safety_response is True
    assert "14416" in card.summary


def test_restricted_topic_is_declined_not_a_crisis(sample_chart):
    card = handle_message("when will I die?", sample_chart, RULES)
    assert card.is_declined is True
    assert card.is_safety_response is False


def test_unclear_message_asks_clarifying_question(sample_chart):
    card = handle_message("hello", sample_chart, RULES)
    assert card.is_clarifying_question is True


def test_normal_topic_question_returns_full_card(sample_chart):
    card = handle_message("how is my career looking?", sample_chart, RULES)
    assert card.topic == "career"
    assert card.summary
    assert card.confidence in ("low", "medium", "high")
    assert card.is_declined is False
    assert card.is_safety_response is False


def test_ai_rewrite_is_none_when_provider_is_none(sample_chart):
    # .env.example defaults AI_PROVIDER to "none"; this must never crash
    # and must leave ai_rewritten_summary unset so the template is used.
    card = handle_message("how is my career looking?", sample_chart, RULES)
    assert card.ai_rewritten_summary is None


def test_followup_question_keeps_previous_topic(sample_chart):
    first = handle_message("how is my marriage looking?", sample_chart, RULES)
    assert first.topic == "marriage"
    second = handle_message("and in 2028?", sample_chart, RULES, previous_topic=first.topic)
    assert second.topic == "marriage"
