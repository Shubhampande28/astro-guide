"""Safety check (CLAUDE.md principle 3). Runs before every reading.

Two separate concerns, deliberately kept apart:

1. Distress/self-harm: if detected, the reading stops entirely and the
   reply is the Tele-MANAS helpline message -- nothing else happens.
2. Restricted topics (death/accident timing, medical diagnosis, legal or
   stock-trading advice): these are declined with a short explanation, but
   are not a crisis response. Handled by `intent.py` classifying the
   message into a RESTRICTED_* topic rather than here, since distinguishing
   "when will I die" (a restricted question) from "I want to die" (a crisis)
   needs to happen before any topic match, not as a second check after.

The keyword lists below are a first pass, not a clinically validated
classifier -- see DECISIONS.md. They deliberately favour catching too much
over too little: a false positive here just shows a caring message with a
helpline, which is a safe failure mode; a false negative is not.
"""

TELE_MANAS_HELPLINE = "14416"

_DISTRESS_PHRASES_EN = [
    "suicide",
    "kill myself",
    "end my life",
    "want to die",
    "better off dead",
    "no reason to live",
    "hurt myself",
    "self harm",
    "self-harm",
    "cutting myself",
    "give up on life",
]

_DISTRESS_PHRASES_HI = [
    "आत्महत्या",
    "खुद को नुकसान",
    "जीना नहीं चाहता",
    "जीना नहीं चाहती",
    "मर जाना चाहता",
    "मर जाना चाहती",
    "खुद को खत्म",
]

_DISTRESS_PHRASES_HINGLISH = [
    "khud ko khatam",
    "khud ko nuksan",
    "jeena nahi chahta",
    "jeena nahi chahti",
    "marna chahta hoon",
    "marna chahti hoon",
    "jaan dena chahta",
    "jaan dena chahti",
    "suicide karna",
    "suicide kar",
]

_ALL_DISTRESS_PHRASES = _DISTRESS_PHRASES_EN + _DISTRESS_PHRASES_HI + _DISTRESS_PHRASES_HINGLISH

_CARE_MESSAGE = {
    "en": (
        "I'm really sorry you're going through this. I'm not able to continue with a "
        "reading right now, but please reach out for support -- you can call or message "
        f"the Tele-MANAS helpline at {TELE_MANAS_HELPLINE}, any time, free, confidential. "
        "You deserve support from a real person, not an astrology app."
    ),
    "hi": (
        "मुझे सुनकर बहुत दुख हुआ कि आप इस स्थिति से गुज़र रहे हैं। मैं अभी कोई भविष्यफल नहीं बता सकता, "
        f"लेकिन कृपया मदद के लिए Tele-MANAS हेल्पलाइन {TELE_MANAS_HELPLINE} पर कॉल करें -- यह हर समय "
        "उपलब्ध, निःशुल्क और गोपनीय है।"
    ),
    "hinglish": (
        "Mujhe sunke bahut dukh hua ki aap is situation se guzar rahe hain. Main abhi koi "
        f"reading nahi de sakta, lekin please Tele-MANAS helpline {TELE_MANAS_HELPLINE} par "
        "call karein -- yeh hamesha available, free aur confidential hai."
    ),
}


def check_distress(message: str) -> bool:
    """True if the message contains distress/self-harm indicators."""
    lowered = message.lower()
    return any(phrase.lower() in lowered for phrase in _ALL_DISTRESS_PHRASES)


def care_message(language: str) -> str:
    return _CARE_MESSAGE.get(language, _CARE_MESSAGE["en"])
