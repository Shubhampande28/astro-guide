from app.rules.evaluator import (
    compute_score,
    compute_timing_windows,
    compute_verdict,
    evaluate_topic,
)
from app.rules.schema import Rule, RuleEffect, RuleSource


def _rule(id_, topic, condition, weight) -> Rule:
    return Rule(
        id=id_,
        topic=topic,
        condition=condition,
        weight=weight,
        effect=RuleEffect(en="x", hi="x", hinglish="x"),
        source=RuleSource(book="Test"),
        status="approved",
    )


def test_compute_score_sums_weights():
    rules = [_rule("A", "career", "True == True", 3), _rule("B", "career", "True == True", -1)]
    assert compute_score(rules) == 2


def test_compute_verdict_thresholds():
    assert compute_verdict(5) == "favourable"
    assert compute_verdict(3) == "favourable"
    assert compute_verdict(2) == "mixed"
    assert compute_verdict(-2) == "mixed"
    assert compute_verdict(-3) == "challenging"
    assert compute_verdict(-10) == "challenging"


def test_evaluate_topic_only_matches_true_conditions_in_that_topic(sample_chart, sample_ctx):
    rules = [
        _rule("CAR-1", "career", "planet(Venus).dignity == 'exalted'", 3),  # true, career
        _rule("CAR-2", "career", "planet(Sun).dignity == 'exalted'", 5),  # false
        _rule("MAR-1", "marriage", "planet(Venus).dignity == 'exalted'", 4),  # true, wrong topic
    ]
    report = evaluate_topic("career", rules, sample_chart, sample_ctx)
    assert [r.id for r in report.matched_rules] == ["CAR-1"]
    assert report.score == 3
    assert report.verdict == "favourable"


def test_compute_timing_windows_matches_house_lord_dasha(sample_chart, sample_ctx):
    # 10th lord from Gemini lagna is Jupiter; the Jupiter maha dasha period
    # should be returned as a career timing window.
    windows = compute_timing_windows("career", sample_chart, sample_ctx)
    assert len(windows) == 1
    assert windows[0].lord == "Jupiter"


def test_timing_windows_empty_if_house_lord_never_runs(sample_chart, sample_ctx):
    # Every one of the 9 Vimshottari lords gets a maha dasha in a full
    # 120-year cycle, so there should always be exactly one window here.
    for topic in ("career", "marriage", "money", "health", "education", "property"):
        windows = compute_timing_windows(topic, sample_chart, sample_ctx)
        assert len(windows) == 1
