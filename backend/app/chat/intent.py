"""Topic + timeframe detection in EN/HI/Hinglish (CLAUDE.md 5.3, F3, F5).

Keyword-first, as CLAUDE.md specifies ("keywords first; small classifier
later" -- the classifier is future work, not Phase 3). Restricted topics
(death/accident timing, medical diagnosis, legal or stock-trading advice,
per principle 3) are detected before the 8 normal topics, since the chat
pipeline must decline these rather than run a reading.
"""

import re
from dataclasses import dataclass

from app.rules.schema import TOPICS

RESTRICTED_TOPICS = ("death", "medical", "legal", "stock")

_RESTRICTED_KEYWORDS: dict[str, list[str]] = {
    "death": [
        "will i die",
        "date of death",
        "death date",
        "accident timing",
        "when will i have an accident",
        "मृत्यु",
        "मरूंगा",
        "मरूँगी",
        "मृत्यु कब",
        "mrityu kab",
        "main kab marunga",
        "main kab marungi",
        "death kab hogi",
    ],
    "medical": [
        "diagnos",
        "cancer",
        "cure for",
        "medical condition",
        "disease hoga",
        "bimari thik",
        "बीमारी ठीक",
        "कैंसर",
        "दवा",
    ],
    "legal": [
        "court case",
        "lawsuit",
        "legal case",
        "will i win the case",
        "मुकदमा",
        "अदालत",
        "mukadma",
        "case jeetunga",
    ],
    "stock": [
        "stock market",
        "share price",
        "which stock",
        "investment tips",
        "crypto",
        "शेयर बाज़ार",
        "शेयर खरीदूं",
        "share kharidu",
        "stock kharidu",
    ],
}

_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "career": [
        "career",
        "job",
        "promotion",
        "business",
        "naukri",
        "naukari",
        "kaam",
        "नौकरी",
        "करियर",
        "व्यापार",
        "काम",
        "job kab milegi",
    ],
    "marriage": [
        "marriage",
        "marry",
        "married",
        "spouse",
        "husband",
        "wife",
        "shaadi",
        "shadi",
        "vivah",
        "विवाह",
        "शादी",
        "पति",
        "पत्नी",
    ],
    "money": [
        "money",
        "wealth",
        "finance",
        "financial",
        "income",
        "paisa",
        "dhan",
        "laabh",
        "धन",
        "पैसा",
        "आय",
        "वित्त",
        "आर्थिक",
    ],
    "health": [
        "health",
        "illness",
        "sick",
        "tabiyat",
        "sehat",
        "सेहत",
        "स्वास्थ्य",
        "बीमार",
    ],
    "education": [
        "study",
        "studies",
        "exam",
        "education",
        "padhai",
        "shiksha",
        "पढ़ाई",
        "शिक्षा",
        "परीक्षा",
    ],
    "foreign_travel": [
        "abroad",
        "foreign",
        "visa",
        "videsh",
        "विदेश",
        "वीज़ा",
        "यात्रा",
    ],
    "children": [
        "child",
        "children",
        "baby",
        "santan",
        "bachche",
        "बच्चे",
        "संतान",
        "बच्चा",
    ],
    "property": [
        "property",
        "house",
        "land",
        "ghar",
        "zameen",
        "संपत्ति",
        "मकान",
        "ज़मीन",
        "जमीन",
    ],
}

_FOLLOWUP_MARKERS = [
    "and in",
    "what about",
    "and what about",
    "uske baad",
    "aur agar",
    "aur uske baad",
    "और उसके बाद",
    "और क्या",
]

_YEAR_PATTERN = re.compile(r"\b(19[5-9]\d|20[0-9]\d|21[0-4]\d)\b")


@dataclass
class Intent:
    topic: str | None  # one of TOPICS, one of RESTRICTED_TOPICS, or None
    year: int | None
    is_followup: bool


def _find_keyword_topic(lowered: str, keywords: dict[str, list[str]]) -> str | None:
    for topic, phrases in keywords.items():
        if any(phrase in lowered for phrase in phrases):
            return topic
    return None


def detect(message: str, previous_topic: str | None = None) -> Intent:
    """Detects topic and timeframe. `previous_topic` supports follow-ups
    like "and in 2028?" that carry no topic keyword of their own."""
    lowered = message.lower()

    year_match = _YEAR_PATTERN.search(lowered)
    year = int(year_match.group(0)) if year_match else None

    restricted = _find_keyword_topic(lowered, _RESTRICTED_KEYWORDS)
    if restricted:
        return Intent(topic=restricted, year=year, is_followup=False)

    topic = _find_keyword_topic(lowered, _TOPIC_KEYWORDS)
    if topic:
        return Intent(topic=topic, year=year, is_followup=False)

    is_followup_phrase = any(marker in lowered for marker in _FOLLOWUP_MARKERS)
    if (is_followup_phrase or year is not None) and previous_topic in TOPICS:
        return Intent(topic=previous_topic, year=year, is_followup=True)

    return Intent(topic=None, year=year, is_followup=False)
