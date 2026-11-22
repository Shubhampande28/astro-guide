from collections import Counter

from app.rules.loader import load_all_rules
from app.rules.schema import TOPICS


def test_loads_200_seed_rules():
    rules = load_all_rules()
    assert len(rules) == 200


def test_25_rules_per_topic():
    rules = load_all_rules()
    counts = Counter(r.topic for r in rules)
    for topic in TOPICS:
        assert counts[topic] == 25


def test_all_rule_ids_unique():
    rules = load_all_rules()
    ids = [r.id for r in rules]
    assert len(ids) == len(set(ids))


def test_all_rules_start_as_draft():
    rules = load_all_rules()
    assert all(r.status == "draft" for r in rules)


def test_no_rule_invents_a_chapter_or_verse():
    # CLAUDE.md 5.2: "Never invent a verse or chapter number."
    rules = load_all_rules()
    assert all(r.source.chapter == "" and r.source.verse == "" for r in rules)
