"""The chat pipeline (CLAUDE.md 5.3): safety -> intent -> rules -> template
-> optional AI rewrite -> verifier -> return.

Steps 3 ("chart from cache") and 8 ("save") are Phase 4 concerns (profiles,
history, DB persistence) and are out of scope here: the chart is passed in
by the caller, and nothing is persisted yet. See DECISIONS.md.
"""

from app.astro.chart import Chart
from app.chat import ai_writer, safety, templates, verifier
from app.chat.intent import RESTRICTED_TOPICS, detect
from app.chat.schemas import AnswerCard
from app.rules.context import ChartContext
from app.rules.evaluator import evaluate_topic
from app.rules.schema import Rule


def handle_message(
    message: str,
    chart: Chart,
    rules: list[Rule],
    language: str = "en",
    previous_topic: str | None = None,
) -> AnswerCard:
    if safety.check_distress(message):
        return AnswerCard(
            topic=None,
            summary=safety.care_message(language),
            why=[],
            sources=[],
            timing=[],
            remedies=[],
            confidence="low",
            language=language,
            is_safety_response=True,
        )

    intent = detect(message, previous_topic)

    if intent.topic in RESTRICTED_TOPICS:
        return templates.build_declined(intent.topic, language)

    if intent.topic is None:
        return templates.build_clarifying_question(language)

    ctx = ChartContext(chart=chart)
    report = evaluate_topic(intent.topic, rules, chart, ctx)
    card = templates.build_topic_answer(intent.topic, report, language, intent.year)

    ai_text = ai_writer.rewrite_summary(
        intent.topic, report.verdict, report.score, card.why, language
    )
    if ai_text is not None and verifier.verify(ai_text, chart):
        card.ai_rewritten_summary = ai_text

    return card
