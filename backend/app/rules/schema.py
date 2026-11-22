"""Rule data model (CLAUDE.md 5.2)."""

from dataclasses import dataclass, field

TOPICS = [
    "career",
    "marriage",
    "money",
    "health",
    "education",
    "foreign_travel",
    "children",
    "property",
]

STATUSES = {"draft", "approved"}


@dataclass
class RuleSource:
    book: str
    chapter: str = ""
    verse: str = ""


@dataclass
class RuleEffect:
    en: str
    hi: str
    hinglish: str


@dataclass
class Rule:
    id: str
    topic: str
    condition: str
    weight: int
    effect: RuleEffect
    source: RuleSource
    remedies: list[str] = field(default_factory=list)
    status: str = "draft"

    def __post_init__(self) -> None:
        if self.topic not in TOPICS:
            raise ValueError(f"{self.id}: unknown topic '{self.topic}'")
        if not -5 <= self.weight <= 5:
            raise ValueError(f"{self.id}: weight {self.weight} out of range -5..5")
        if self.status not in STATUSES:
            raise ValueError(f"{self.id}: unknown status '{self.status}'")
