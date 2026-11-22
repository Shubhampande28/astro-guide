"""Phase 3 "done when" criterion (CLAUDE.md Phase 7 table): the 50-question
test set must score >=90% correct topic detection and 0 safety failures.
"""

from app.chat.intent import detect
from app.chat.safety import check_distress
from tests.chat.fifty_question_test_set import QUESTIONS

ACCURACY_THRESHOLD = 0.90

# The last entry is the follow-up case; it needs previous_topic context
# that the other 49 don't, so it's handled separately below.
_FOLLOWUP_INDEX = len(QUESTIONS) - 1


def test_topic_detection_accuracy_at_least_90_percent():
    correct = 0
    mismatches = []

    for i, (message, expected_topic, _is_distress) in enumerate(QUESTIONS):
        previous_topic = "career" if i == _FOLLOWUP_INDEX else None
        actual_topic = detect(message, previous_topic=previous_topic).topic
        if actual_topic == expected_topic:
            correct += 1
        else:
            mismatches.append((message, expected_topic, actual_topic))

    accuracy = correct / len(QUESTIONS)
    assert (
        accuracy >= ACCURACY_THRESHOLD
    ), f"Accuracy {accuracy:.1%} below {ACCURACY_THRESHOLD:.0%}. Mismatches: {mismatches}"


def test_zero_safety_failures():
    """Every distress case must be caught, and nothing else must be
    mistaken for one."""
    failures = []
    for message, _expected_topic, is_distress in QUESTIONS:
        detected = check_distress(message)
        if detected != is_distress:
            failures.append((message, "expected_distress" if is_distress else "false_positive"))

    assert failures == [], f"Safety failures: {failures}"
