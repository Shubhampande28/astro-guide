"""The 6-part answer card (CLAUDE.md F3): Summary, Why, Sources, Timing,
Remedies, Confidence.
"""

from dataclasses import dataclass, field


@dataclass
class AnswerCard:
    topic: str | None
    summary: str
    why: list[str]
    sources: list[str]
    timing: list[str]
    remedies: list[str]
    confidence: str  # "high" | "medium" | "low"
    language: str
    is_safety_response: bool = False
    is_declined: bool = False
    is_clarifying_question: bool = False
    ai_rewritten_summary: str | None = field(default=None)
