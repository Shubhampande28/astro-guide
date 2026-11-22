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


def test_unclear_message_has_no_topic():
    assert detect("hello").topic is None


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
