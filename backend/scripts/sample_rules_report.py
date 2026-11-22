"""Phase 2 deliverable: a sample rules report for 3 charts.

Prints, for each of 3 sample births and each of the 8 topics: which rules
matched, the score, the verdict, and the dasha timing windows. All 200 seed
rules are still status: draft (no astrologer has approved any yet, since
the admin panel is Phase 9), so this report evaluates every rule
regardless of status -- real user-facing answers will filter to approved
rules only once that panel exists (see DECISIONS.md).

Run with (from backend/): python -m scripts.sample_rules_report
"""

from datetime import date, time

from app.astro.chart import compute_chart
from app.rules.context import ChartContext
from app.rules.evaluator import evaluate_topic
from app.rules.loader import load_all_rules
from app.rules.schema import TOPICS

SAMPLE_BIRTHS = [
    ("1990 New Delhi", date(1990, 5, 15), time(8, 30), "Asia/Kolkata", 28.6139, 77.2090),
    ("1943 Bombay (wartime IST)", date(1943, 3, 1), time(6, 30), "Asia/Kolkata", 18.9388, 72.8354),
    (
        "2005 Sydney (southern hemisphere)",
        date(2005, 7, 20),
        time(12, 0),
        "Australia/Sydney",
        -33.8688,
        151.2093,
    ),
]


def main() -> None:
    rules = load_all_rules()
    print(f"Loaded {len(rules)} seed rules.\n")

    for label, birth_date, birth_time, tz_name, lat, lon in SAMPLE_BIRTHS:
        chart = compute_chart(birth_date, birth_time, tz_name, lat, lon)
        ctx = ChartContext(chart=chart)

        print("=" * 70)
        print(f"{label}: {birth_date} {birth_time} ({tz_name}, {lat}, {lon})")
        print(
            f"Lagna: {chart.lagna.sign} | Current dasha: {chart.current_maha_dasha}/{chart.current_antar_dasha}"
        )
        print("=" * 70)

        for topic in TOPICS:
            report = evaluate_topic(topic, list(rules), chart, ctx)
            print(f"\n-- {topic} -- score={report.score} verdict={report.verdict}")
            for rule in report.matched_rules:
                print(f"   [{rule.id}] ({rule.weight:+d}) {rule.effect.en}")
            for window in report.timing_windows:
                print(
                    f"   timing: {window.lord} dasha, {window.start.date()} to {window.end.date()}"
                )
        print()


if __name__ == "__main__":
    main()
