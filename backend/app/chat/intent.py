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
        "promoted",
        "business",
        "work",
        "profession",
        "employment",
        "unemployed",
        "interview",
        "appraisal",
        "resign",
        "resignation",
        "switch job",
        "new job",
        "startup",
        "boss",
        "office",
        "posting",
        "transfer",
        "govt job",
        "government job",
        "sarkari naukri",
        "naukri",
        "naukari",
        "kaam",
        "नौकरी",
        "करियर",
        "व्यापार",
        "काम",
        "तरक्की",
        "तरक्की कब",
        "job kab milegi",
        "promotion kab",
        "tarakki",
    ],
    "marriage": [
        "marriage",
        "marry",
        "married",
        "wedding",
        "spouse",
        "husband",
        "wife",
        "fiance",
        "fiancee",
        "engagement",
        "engaged",
        "love marriage",
        "arranged marriage",
        "partner",
        "boyfriend",
        "girlfriend",
        "relationship",
        "divorce",
        "shaadi",
        "shadi",
        "vivah",
        "rishta",
        "विवाह",
        "शादी",
        "पति",
        "पत्नी",
        "सगाई",
        "रिश्ता",
    ],
    "money": [
        "money",
        "wealth",
        "wealthy",
        "rich",
        "richer",
        "finance",
        "financial",
        "income",
        "salary",
        "savings",
        "loan",
        "debt",
        "lottery",
        "bonus",
        "hike",
        "increment",
        "profit",
        "loss",
        "earn",
        "earning",
        "afford",
        "paisa",
        "paise",
        "dhan",
        "laabh",
        "ameer",
        "amir",
        "kamai",
        "dhan prapti",
        "धन",
        "पैसा",
        "पैसे",
        "आय",
        "वित्त",
        "आर्थिक",
        "अमीर",
        "कमाई",
        "लॉटरी",
    ],
    "health": [
        "health",
        "illness",
        "ill",
        "sick",
        "disease",
        "fitness",
        "recover",
        "recovery",
        "surgery",
        "wellbeing",
        "well-being",
        "tabiyat",
        "sehat",
        "सेहत",
        "स्वास्थ्य",
        "बीमार",
        "तबीयत",
    ],
    "education": [
        "study",
        "studies",
        "studying",
        "exam",
        "exams",
        "education",
        "college",
        "university",
        "admission",
        "degree",
        "result",
        "results",
        "marks",
        "padhai",
        "shiksha",
        "पढ़ाई",
        "शिक्षा",
        "परीक्षा",
        "कॉलेज",
        "दाखिला",
    ],
    "foreign_travel": [
        "abroad",
        "foreign",
        "visa",
        "immigration",
        "immigrate",
        "migrate",
        "relocate",
        "settle abroad",
        "settle overseas",
        "overseas",
        "videsh",
        "pravaas",
        "विदेश",
        "वीज़ा",
        "यात्रा",
        "प्रवास",
    ],
    "children": [
        "child",
        "children",
        "kids",
        "baby",
        "pregnant",
        "pregnancy",
        "conceive",
        "santan",
        "bachche",
        "bachcha",
        "संतान",
        "बच्चे",
        "बच्चा",
        "गर्भ",
        "गर्भवती",
    ],
    "property": [
        "property",
        "house",
        "home",
        "flat",
        "apartment",
        "land",
        "plot",
        "real estate",
        "buy a house",
        "buying a house",
        "ghar",
        "makaan",
        "zameen",
        "जमीन",
        "संपत्ति",
        "मकान",
        "ज़मीन",
        "फ्लैट",
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


def _compile_keyword_patterns(
    keywords: dict[str, list[str]],
) -> dict[str, list[re.Pattern[str]]]:
    # Word-boundary matching, not plain substring: otherwise a short keyword
    # like "ill" (health) would false-positive inside "will" ("will I...?"),
    # silently misrouting almost every question into the wrong topic.
    return {
        topic: [re.compile(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)") for phrase in phrases]
        for topic, phrases in keywords.items()
    }


_RESTRICTED_PATTERNS = _compile_keyword_patterns(_RESTRICTED_KEYWORDS)
_TOPIC_PATTERNS = _compile_keyword_patterns(_TOPIC_KEYWORDS)


def _find_keyword_topic(lowered: str, patterns: dict[str, list[re.Pattern[str]]]) -> str | None:
    for topic, compiled in patterns.items():
        if any(pattern.search(lowered) for pattern in compiled):
            return topic
    return None


def detect(message: str, previous_topic: str | None = None) -> Intent:
    """Detects topic and timeframe. `previous_topic` supports follow-ups
    like "and in 2028?" that carry no topic keyword of their own."""
    lowered = message.lower()

    year_match = _YEAR_PATTERN.search(lowered)
    year = int(year_match.group(0)) if year_match else None

    restricted = _find_keyword_topic(lowered, _RESTRICTED_PATTERNS)
    if restricted:
        return Intent(topic=restricted, year=year, is_followup=False)

    topic = _find_keyword_topic(lowered, _TOPIC_PATTERNS)
    if topic:
        return Intent(topic=topic, year=year, is_followup=False)

    is_followup_phrase = any(marker in lowered for marker in _FOLLOWUP_MARKERS)
    if (is_followup_phrase or year is not None) and previous_topic in TOPICS:
        return Intent(topic=previous_topic, year=year, is_followup=True)

    return Intent(topic=None, year=year, is_followup=False)
