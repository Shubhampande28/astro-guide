from app.chat.safety import TELE_MANAS_HELPLINE, care_message, check_distress


def test_detects_english_distress():
    assert check_distress("I want to kill myself") is True
    assert check_distress("sometimes I think about suicide") is True


def test_detects_hindi_distress():
    assert check_distress("मैं आत्महत्या करना चाहता हूं") is True


def test_detects_hinglish_distress():
    assert check_distress("main marna chahta hoon") is True
    assert check_distress("khud ko nuksan pahunchana chahta hoon") is True


def test_does_not_false_positive_on_normal_questions():
    assert check_distress("when will I get a job?") is False
    assert check_distress("shaadi kab hogi?") is False
    assert check_distress("मेरा करियर कैसा रहेगा?") is False
    # "marriage" and "marna" (to die) share no substring, but check a
    # near-miss anyway: asking about death timing is not self-harm.
    assert check_distress("when will I die") is False


def test_care_message_includes_helpline_in_all_languages():
    for language in ("en", "hi", "hinglish"):
        assert TELE_MANAS_HELPLINE in care_message(language)
