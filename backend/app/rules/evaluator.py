"""Evaluates a topic's rules against a chart: matched rules, score, verdict,
and timing windows.

Timing windows are a deliberate simplification: each topic is mapped to one
primary classical house (career=10th, marriage=7th, etc.), and the timing
windows returned are the Vimshottari maha dasha periods whose lord rules
that house -- the classical method for "when will X happen". A rule's
condition can reference several houses/planets, and extracting "the"
relevant house generically from an arbitrary DSL expression isn't
well-defined, so this topic-level house is used instead. See DECISIONS.md.
"""

from dataclasses import dataclass
from datetime import datetime

from app.astro.chart import Chart
from app.rules.context import ChartContext
from app.rules.dsl import evaluate, parse
from app.rules.schema import Rule

TOPIC_PRIMARY_HOUSE = {
    "career": 10,
    "marriage": 7,
    "money": 2,
    "health": 6,
    "education": 5,
    "foreign_travel": 12,
    "children": 5,
    "property": 4,
}

FAVOURABLE_THRESHOLD = 3
CHALLENGING_THRESHOLD = -3


@dataclass
class TimingWindow:
    lord: str
    start: datetime
    end: datetime


@dataclass
class TopicReport:
    topic: str
    matched_rules: list[Rule]
    score: int
    verdict: str
    timing_windows: list[TimingWindow]


def match_rules(rules: list[Rule], ctx: ChartContext) -> list[Rule]:
    matched = []
    for rule in rules:
        tree = parse(rule.condition)
        if evaluate(tree, ctx):
            matched.append(rule)
    return matched


def compute_score(matched_rules: list[Rule]) -> int:
    return sum(rule.weight for rule in matched_rules)


def compute_verdict(score: int) -> str:
    if score >= FAVOURABLE_THRESHOLD:
        return "favourable"
    if score <= CHALLENGING_THRESHOLD:
        return "challenging"
    return "mixed"


def compute_timing_windows(topic: str, chart: Chart, ctx: ChartContext) -> list[TimingWindow]:
    house = TOPIC_PRIMARY_HOUSE[topic]
    house_lord = ctx.lord_of(house)
    windows = []
    for maha in chart.vimshottari:
        if maha.lord == house_lord:
            windows.append(TimingWindow(lord=maha.lord, start=maha.start, end=maha.end))
    return windows


def evaluate_topic(topic: str, rules: list[Rule], chart: Chart, ctx: ChartContext) -> TopicReport:
    topic_rules = [r for r in rules if r.topic == topic]
    matched = match_rules(topic_rules, ctx)
    score = compute_score(matched)
    return TopicReport(
        topic=topic,
        matched_rules=matched,
        score=score,
        verdict=compute_verdict(score),
        timing_windows=compute_timing_windows(topic, chart, ctx),
    )
