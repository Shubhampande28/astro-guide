"""Builds the 6-part AnswerCard from a rules TopicReport, or from a
restricted-topic decline / clarifying-question, in EN/HI/Hinglish.

This is the template path CLAUDE.md 5.3 describes: "If AI is off or fails,
templates write the answer." It must always produce a complete, correct
answer on its own -- the optional AI rewrite (app/chat/ai_writer.py) only
ever polishes `summary`, never replaces Why/Sources/Timing/Remedies.
"""

from app.chat.schemas import AnswerCard
from app.rules.evaluator import TopicReport

TOPIC_DISPLAY = {
    "career": {"en": "career", "hi": "करियर", "hinglish": "career"},
    "marriage": {"en": "marriage", "hi": "विवाह", "hinglish": "shaadi"},
    "money": {"en": "money", "hi": "धन", "hinglish": "paisa"},
    "health": {"en": "health", "hi": "स्वास्थ्य", "hinglish": "health"},
    "education": {"en": "education", "hi": "शिक्षा", "hinglish": "padhai"},
    "foreign_travel": {"en": "foreign travel", "hi": "विदेश यात्रा", "hinglish": "videsh yatra"},
    "children": {"en": "children", "hi": "संतान", "hinglish": "bachche"},
    "property": {"en": "property", "hi": "संपत्ति", "hinglish": "property"},
}

_VERDICT_SUMMARY = {
    "favourable": {
        "en": "Your {topic} outlook looks favourable overall.",
        "hi": "आपका {topic} दृष्टिकोण समग्र रूप से अनुकूल दिख रहा है।",
        "hinglish": "Aapka {topic} outlook overall favourable dikh raha hai.",
    },
    "mixed": {
        "en": "Your {topic} outlook looks mixed -- some support, some challenges.",
        "hi": "आपका {topic} दृष्टिकोण मिश्रित है -- कुछ सहायक और कुछ चुनौतीपूर्ण संकेत हैं।",
        "hinglish": "Aapka {topic} outlook mixed hai -- kuch support, kuch challenges.",
    },
    "challenging": {
        "en": "Your {topic} outlook looks challenging right now.",
        "hi": "आपका {topic} दृष्टिकोण अभी चुनौतीपूर्ण दिख रहा है।",
        "hinglish": "Aapka {topic} outlook abhi challenging dikh raha hai.",
    },
}

_NO_MATCH_SUMMARY = {
    "en": "Nothing strongly stands out for {topic} in your chart right now.",
    "hi": "इस समय आपकी कुंडली में {topic} के लिए कुछ विशेष संकेत नहीं मिला।",
    "hinglish": "Abhi aapki kundli mein {topic} ke liye kuch khaas signal nahi mila.",
}

_CLARIFYING_QUESTION = {
    "en": "I didn't quite catch what you'd like to know -- could you ask about a specific "
    "topic, like career, marriage, money, health, education, foreign travel, children, "
    "or property?",
    "hi": "मुझे ठीक से समझ नहीं आया कि आप क्या जानना चाहते हैं -- कृपया करियर, विवाह, धन, स्वास्थ्य, "
    "शिक्षा, विदेश यात्रा, संतान या संपत्ति में से किसी विषय के बारे में पूछें।",
    "hinglish": "Mujhe samajh nahi aaya aap kya jaanna chahte hain -- please career, shaadi, "
    "paisa, health, padhai, videsh yatra, bachche, ya property mein se kisi topic ke baare "
    "mein poochein.",
}

_DECLINE_MESSAGES = {
    "death": {
        "en": "I don't give predictions about death or accident timing -- that's not something "
        "astrology should be used for here, and it's not a question I'll answer.",
        "hi": "मैं मृत्यु या दुर्घटना के समय के बारे में कोई भविष्यवाणी नहीं करता -- यह ऐसा सवाल नहीं है "
        "जिसका मैं जवाब दूंगा।",
        "hinglish": "Main death ya accident ke timing ke baare mein koi prediction nahi deta -- "
        "yeh ek aisa sawaal nahi hai jiska main jawab doonga.",
    },
    "medical": {
        "en": "I can't diagnose health conditions or predict disease outcomes -- please see a "
        "doctor for that. I can talk about general wellbeing trends if you'd like.",
        "hi": "मैं किसी बीमारी का निदान या परिणाम नहीं बता सकता -- कृपया डॉक्टर से मिलें। चाहें तो मैं "
        "सामान्य स्वास्थ्य रुझान बता सकता हूं।",
        "hinglish": "Main kisi bimari ka diagnosis ya outcome nahi bata sakta -- please doctor se "
        "milein. Chahein toh main general health trends bata sakta hoon.",
    },
    "legal": {
        "en": "I don't give predictions about legal cases or court outcomes -- please consult a "
        "lawyer for that.",
        "hi": "मैं कानूनी मामलों या अदालत के फैसलों के बारे में भविष्यवाणी नहीं करता -- कृपया वकील से "
        "सलाह लें।",
        "hinglish": "Main legal cases ya court ke outcome ke baare mein prediction nahi deta -- "
        "please lawyer se consult karein.",
    },
    "stock": {
        "en": "I don't give stock market or investment advice -- please consult a licensed "
        "financial advisor for that.",
        "hi": "मैं शेयर बाज़ार या निवेश की सलाह नहीं देता -- कृपया किसी लाइसेंस प्राप्त वित्तीय सलाहकार "
        "से बात करें।",
        "hinglish": "Main stock market ya investment advice nahi deta -- please kisi licensed "
        "financial advisor se baat karein.",
    },
}


def build_clarifying_question(language: str) -> AnswerCard:
    text = _CLARIFYING_QUESTION.get(language, _CLARIFYING_QUESTION["en"])
    return AnswerCard(
        topic=None,
        summary=text,
        why=[],
        sources=[],
        timing=[],
        remedies=[],
        confidence="low",
        language=language,
        is_clarifying_question=True,
    )


def build_declined(restricted_topic: str, language: str) -> AnswerCard:
    text = _DECLINE_MESSAGES[restricted_topic].get(
        language, _DECLINE_MESSAGES[restricted_topic]["en"]
    )
    return AnswerCard(
        topic=restricted_topic,
        summary=text,
        why=[],
        sources=[],
        timing=[],
        remedies=[],
        confidence="low",
        language=language,
        is_declined=True,
    )


def _confidence(report: TopicReport) -> str:
    if not report.matched_rules:
        return "low"
    if abs(report.score) >= 5:
        return "high"
    return "medium"


def _timing_sentences(report: TopicReport, language: str, year: int | None) -> list[str]:
    sentences = []
    for window in report.timing_windows:
        start_year, end_year = window.start.year, window.end.year
        in_window = year is not None and start_year <= year <= end_year
        if language == "hi":
            s = f"{window.lord} दशा ({start_year}-{end_year}) इस विषय को सक्रिय करती है।"
            if in_window:
                s += f" {year} इस अवधि के भीतर आता है।"
        elif language == "hinglish":
            s = f"{window.lord} dasha ({start_year}-{end_year}) is topic ko activate karti hai."
            if in_window:
                s += f" {year} isi period ke andar aata hai."
        else:
            s = f"The {window.lord} dasha ({start_year}-{end_year}) activates this topic."
            if in_window:
                s += f" {year} falls within this period."
        sentences.append(s)
    return sentences


def build_topic_answer(
    topic: str, report: TopicReport, language: str, year: int | None = None
) -> AnswerCard:
    noun = TOPIC_DISPLAY[topic].get(language, TOPIC_DISPLAY[topic]["en"])

    if report.matched_rules:
        summary_template = _VERDICT_SUMMARY[report.verdict].get(
            language, _VERDICT_SUMMARY[report.verdict]["en"]
        )
    else:
        summary_template = _NO_MATCH_SUMMARY.get(language, _NO_MATCH_SUMMARY["en"])
    summary = summary_template.format(topic=noun)

    why = [
        (
            rule.effect.hi
            if language == "hi"
            else rule.effect.hinglish if language == "hinglish" else rule.effect.en
        )
        for rule in report.matched_rules
    ]
    sources = sorted({rule.source.book for rule in report.matched_rules})
    remedies = sorted({r for rule in report.matched_rules for r in rule.remedies})
    timing = _timing_sentences(report, language, year)

    return AnswerCard(
        topic=topic,
        summary=summary,
        why=why,
        sources=sources,
        timing=timing,
        remedies=remedies,
        confidence=_confidence(report),
        language=language,
    )
