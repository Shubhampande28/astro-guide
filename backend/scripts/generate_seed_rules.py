"""Generates the 200 Phase 2 seed rules (25 per topic x 8 topics) into
rules_data/*.yaml.

This is a one-off content generator, not part of the running app. It exists
because hand-writing 200 individually distinct rules isn't a good use of
time versus encoding the *pattern* once: each topic gets the same 25-slot
template (house placement of its house lord, its classical karaka's
dignity, aspects, conjunctions, dasha activation), with the astrology
(which house/karaka/weights) chosen per topic below. All rules are seeded
as status: draft, per CLAUDE.md 5.2 -- an astrologer reviews and approves
them via the admin panel (F15, Phase 9) before they reach paying users.
No chapter/verse numbers are invented; only the source book is named.

Re-run with: python scripts/generate_seed_rules.py
"""

from pathlib import Path

import yaml

RULES_DATA_DIR = Path(__file__).resolve().parent.parent / "rules_data"

# General "placement strength" of a house, independent of topic: trikona
# (1,5,9) and kendra (4,7,10) are classically the strongest, upachaya
# (3,6,11) support growth, and dusthana (6,8,12) are challenging. House 6
# appears in both upachaya and dusthana traditions; here it is treated as
# dusthana (its first and most common classical reading).
HOUSE_WEIGHT = {1: 4, 2: 1, 3: 2, 4: 3, 5: 4, 6: -3, 7: 3, 8: -4, 9: 4, 10: 3, 11: 2, 12: -2}

TOPICS = {
    "career": {
        "prefix": "CAR",
        "house": 10,
        "karaka": "Saturn",
        "karaka_hi": "शनि",
        "secondary": "Sun",
        "secondary_hi": "सूर्य",
        "noun_en": "career",
        "noun_hi": "करियर",
        "noun_hinglish": "career",
    },
    "marriage": {
        "prefix": "MAR",
        "house": 7,
        "karaka": "Venus",
        "karaka_hi": "शुक्र",
        "secondary": "Jupiter",
        "secondary_hi": "गुरु",
        "noun_en": "marriage",
        "noun_hi": "विवाह",
        "noun_hinglish": "shaadi",
    },
    "money": {
        "prefix": "MON",
        "house": 2,
        "karaka": "Jupiter",
        "karaka_hi": "गुरु",
        "secondary": "Venus",
        "secondary_hi": "शुक्र",
        "noun_en": "wealth",
        "noun_hi": "धन",
        "noun_hinglish": "paisa",
    },
    "health": {
        "prefix": "HEA",
        "house": 6,
        "karaka": "Moon",
        "karaka_hi": "चंद्र",
        "secondary": "Mars",
        "secondary_hi": "मंगल",
        "noun_en": "health",
        "noun_hi": "स्वास्थ्य",
        "noun_hinglish": "health",
    },
    "education": {
        "prefix": "EDU",
        "house": 5,
        "karaka": "Mercury",
        "karaka_hi": "बुध",
        "secondary": "Jupiter",
        "secondary_hi": "गुरु",
        "noun_en": "education",
        "noun_hi": "शिक्षा",
        "noun_hinglish": "padhai",
    },
    "foreign_travel": {
        "prefix": "FOR",
        "house": 12,
        "karaka": "Rahu",
        "karaka_hi": "राहु",
        "secondary": "Moon",
        "secondary_hi": "चंद्र",
        "noun_en": "foreign travel",
        "noun_hi": "विदेश यात्रा",
        "noun_hinglish": "videsh yatra",
    },
    "children": {
        "prefix": "CHI",
        "house": 5,
        "karaka": "Jupiter",
        "karaka_hi": "गुरु",
        "secondary": "Sun",
        "secondary_hi": "सूर्य",
        "noun_en": "children",
        "noun_hi": "संतान",
        "noun_hinglish": "bachche",
    },
    "property": {
        "prefix": "PRO",
        "house": 4,
        "karaka": "Mars",
        "karaka_hi": "मंगल",
        "secondary": "Saturn",
        "secondary_hi": "शनि",
        "noun_en": "property",
        "noun_hi": "संपत्ति",
        "noun_hinglish": "property",
    },
}

SOURCE_BOOK = "Brihat Parashara Hora Shastra"


def _rule(id_, topic, condition, weight, en, hi, hinglish):
    return {
        "id": id_,
        "topic": topic,
        "condition": condition,
        "weight": weight,
        "effect": {"en": en, "hi": hi, "hinglish": hinglish},
        "source": {"book": SOURCE_BOOK, "chapter": "", "verse": ""},
        "remedies": [],
        "status": "draft",
    }


def _house_ordinal(n: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n, f"{n}th")


def generate_topic_rules(topic: str, meta: dict) -> list[dict]:
    house = meta["house"]
    karaka = meta["karaka"]
    secondary = meta["secondary"]
    noun = meta["noun_en"]
    noun_hi = meta["noun_hi"]
    noun_hinglish = meta["noun_hinglish"]
    prefix = meta["prefix"]
    rules = []
    n = 0

    # A. House-lord placement (12 rules): lord(house) in house(X) for every X.
    for x in range(1, 13):
        n += 1
        weight = HOUSE_WEIGHT[x]
        tone = (
            "supports"
            if weight > 0
            else "creates obstacles for" if weight < 0 else "has a mixed effect on"
        )
        ordinal = _house_ordinal(x)
        rules.append(
            _rule(
                f"{prefix}-{n:03d}",
                topic,
                f"lord({house}) in house({x})",
                weight,
                f"The lord of the {_house_ordinal(house)} house placed in the {ordinal} house {tone} {noun}.",
                f"{_house_ordinal(house)} भाव का स्वामी {ordinal} भाव में होने से {noun_hi} पर प्रभाव पड़ता है।",
                f"{_house_ordinal(house)} house ka swami {ordinal} house mein hone se {noun_hinglish} par asar padta hai.",
            )
        )

    # B. Primary karaka dignity (4 rules).
    for dignity, weight, label in [
        ("exalted", 4, "strongly favours"),
        ("own", 2, "supports"),
        ("moolatrikona", 3, "favours"),
        ("debilitated", -4, "weakens"),
    ]:
        n += 1
        rules.append(
            _rule(
                f"{prefix}-{n:03d}",
                topic,
                f"planet({karaka}).dignity == '{dignity}'",
                weight,
                f"{karaka}, the significator of {noun}, is {dignity} and {label} matters of {noun}.",
                f"{meta['karaka_hi']} {noun_hi} का कारक है और {dignity} होने से इस पर असर पड़ता है।",
                f"{karaka}, {noun_hinglish} ka karaka, {dignity} hai aur isse {noun_hinglish} par asar padta hai.",
            )
        )

    # C. Secondary karaka dignity (2 rules).
    for dignity, weight in [("exalted", 3), ("debilitated", -3)]:
        n += 1
        rules.append(
            _rule(
                f"{prefix}-{n:03d}",
                topic,
                f"planet({secondary}).dignity == '{dignity}'",
                weight,
                f"{secondary}, a secondary significator of {noun}, is {dignity}, affecting {noun}.",
                f"{meta['secondary_hi']} भी {noun_hi} का एक कारक है और {dignity} होने से असर होता है।",
                f"{secondary}, {noun_hinglish} ka secondary karaka, {dignity} hai, isse bhi asar padta hai.",
            )
        )

    # D. Primary karaka retrograde (1 rule).
    n += 1
    rules.append(
        _rule(
            f"{prefix}-{n:03d}",
            topic,
            f"planet({karaka}).retro == True",
            -1,
            f"{karaka} retrograde can delay outcomes related to {noun}, though the eventual result is not ruled out.",
            f"{meta['karaka_hi']} वक्री होने से {noun_hi} से जुड़े परिणामों में देरी हो सकती है।",
            f"{karaka} vakri hone se {noun_hinglish} se related results mein deri ho sakti hai.",
        )
    )

    # E. Aspects on the topic house from Jupiter (benefic) and Saturn (malefic).
    for planet, weight, label in [
        ("Jupiter", 3, "a protective, favourable"),
        ("Saturn", -2, "a restrictive"),
    ]:
        n += 1
        rules.append(
            _rule(
                f"{prefix}-{n:03d}",
                topic,
                f"aspects({planet}, {house})",
                weight,
                f"{planet} aspecting the {_house_ordinal(house)} house brings {label} influence on {noun}.",
                f"{planet} की {_house_ordinal(house)} भाव पर दृष्टि {noun_hi} को प्रभावित करती है।",
                f"{planet} ki {_house_ordinal(house)} house par drishti {noun_hinglish} ko asar karti hai.",
            )
        )

    # F. House lord conjunct a benefic/malefic.
    for planet, weight, label in [("Jupiter", 3, "benefic"), ("Saturn", -2, "challenging")]:
        n += 1
        rules.append(
            _rule(
                f"{prefix}-{n:03d}",
                topic,
                f"conj(lord({house}), {planet})",
                weight,
                f"The {_house_ordinal(house)} lord conjunct {planet} brings a {label} influence on {noun}.",
                f"{_house_ordinal(house)} भाव का स्वामी {planet} के साथ होने से {noun_hi} पर असर पड़ता है।",
                f"{_house_ordinal(house)} house ka swami {planet} ke saath hone se {noun_hinglish} par asar padta hai.",
            )
        )

    # G. Dasha activation of the primary karaka.
    for attr, weight in [("maha", 2), ("antar", 1)]:
        n += 1
        rules.append(
            _rule(
                f"{prefix}-{n:03d}",
                topic,
                f"dasha.{attr} == '{karaka}'",
                weight,
                f"The current {karaka} dasha activates matters of {noun}.",
                f"चल रही {meta['karaka_hi']} दशा {noun_hi} से जुड़े विषयों को सक्रिय करती है।",
                f"Chal rahi {karaka} dasha {noun_hinglish} se related topics ko activate karti hai.",
            )
        )

    assert n == 25, f"{topic}: expected 25 rules, got {n}"
    return rules


def main() -> None:
    RULES_DATA_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for topic, meta in TOPICS.items():
        rules = generate_topic_rules(topic, meta)
        out_path = RULES_DATA_DIR / f"{topic}.yaml"
        with open(out_path, "w", encoding="utf-8") as f:
            yaml.dump(rules, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"wrote {len(rules)} rules to {out_path}")
        total += len(rules)
    print(f"total: {total} rules")


if __name__ == "__main__":
    main()
