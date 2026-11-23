from app.chat import ai_writer
from app.chat.intent import detect


def test_detects_career_english():
    assert detect("when will I get a promotion?").topic == "career"


def test_detects_marriage_hindi():
    assert detect("मेरी शादी कब होगी?").topic == "marriage"


def test_detects_money_hinglish():
    assert detect("mera paisa kaise rahega is saal?").topic == "money"


def test_detects_restricted_death_topic():
    assert detect("when will I die?").topic == "death"


def test_detects_restricted_medical_topic():
    assert detect("will my cancer be cured?").topic == "medical"


def test_detects_restricted_legal_topic():
    assert detect("will I win my court case?").topic == "legal"


def test_detects_restricted_stock_topic():
    assert detect("which stock should I buy?").topic == "stock"


def test_unclear_message_has_no_topic(monkeypatch):
    # Force the AI classifier fallback off so this stays deterministic
    # regardless of whether a real AI_PROVIDER is configured in .env.
    monkeypatch.setattr(ai_writer, "classify_topic", lambda message, topics: None)
    assert detect("hello").topic is None


def test_unkeyworded_phrasing_falls_back_to_ai_classification(monkeypatch):
    monkeypatch.setattr(ai_writer, "classify_topic", lambda message, topics: "marriage")
    assert detect("how's my love life looking these days").topic == "marriage"


def test_ai_classifier_can_still_route_into_a_restricted_topic(monkeypatch):
    # Safety-critical: a phrasing with no restricted keyword must still be
    # caught if the AI classifier recognizes it, not slip through to a
    # normal reading just because it skipped the keyword list.
    monkeypatch.setattr(ai_writer, "classify_topic", lambda message, topics: "medical")
    assert detect("will this thing on my skin ever go away").topic == "medical"


def test_ai_classifier_unsure_still_falls_back_to_clarifying(monkeypatch):
    monkeypatch.setattr(ai_writer, "classify_topic", lambda message, topics: None)
    assert detect("asdkjasdkj").topic is None


def test_detects_money_for_everyday_phrasing_not_just_the_word_money():
    assert detect("Will I become rich suddenly?").topic == "money"
    assert detect("Any chance of winning the lottery?").topic == "money"
    assert detect("will I get a salary hike this year?").topic == "money"


def test_detects_career_for_everyday_phrasing_not_just_the_word_career():
    assert detect("should I resign from my current job?").topic == "career"
    assert detect("will I get transferred to another office?").topic == "career"


def test_detects_marriage_for_everyday_phrasing():
    assert detect("will my engagement happen this year?").topic == "marriage"
    assert detect("how is my relationship with my partner?").topic == "marriage"


def test_detects_property_for_everyday_phrasing():
    assert detect("should I buy a flat this year?").topic == "property"


def test_detects_foreign_travel_for_everyday_phrasing():
    assert detect("will I be able to settle abroad?").topic == "foreign_travel"


def test_detects_children_for_everyday_phrasing():
    assert detect("when will we conceive?").topic == "children"


def test_detects_education_for_everyday_phrasing():
    assert detect("will I get admission in a good college?").topic == "education"


def test_extracts_year():
    intent = detect("how is my career in 2028?")
    assert intent.topic == "career"
    assert intent.year == 2028


def test_followup_keeps_previous_topic():
    intent = detect("and in 2028?", previous_topic="career")
    assert intent.topic == "career"
    assert intent.year == 2028
    assert intent.is_followup is True


def test_followup_without_previous_topic_is_unclear():
    intent = detect("and in 2028?", previous_topic=None)
    assert intent.topic is None
