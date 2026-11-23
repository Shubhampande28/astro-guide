import pytest

from app.chat import ai_writer
from app.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_returns_none_when_provider_is_none(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "none")
    result = ai_writer.rewrite_summary("career", "favourable", 5, ["effect"], "en")
    assert result is None


def test_returns_none_when_api_key_missing(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CLAUDE_API_KEY", "")
    result = ai_writer.rewrite_summary("career", "favourable", 5, ["effect"], "en")
    assert result is None


def test_returns_none_when_no_rule_effects(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CLAUDE_API_KEY", "fake-key")
    result = ai_writer.rewrite_summary("career", "favourable", 5, [], "en")
    assert result is None


def test_calls_claude_and_never_sends_pii(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CLAUDE_API_KEY", "fake-key")

    captured = {}

    def fake_post_json(url, headers, payload):
        captured["url"] = url
        captured["payload"] = payload
        return {"content": [{"text": "A rewritten paragraph."}]}

    monkeypatch.setattr(ai_writer, "_post_json", fake_post_json)

    result = ai_writer.rewrite_summary(
        "career", "favourable", 5, ["The 10th lord is well placed."], "en"
    )
    assert result == "A rewritten paragraph."
    assert "anthropic.com" in captured["url"]
    prompt_text = str(captured["payload"])
    assert "10th lord" in prompt_text
    # No name or birth details are ever part of the prompt payload.
    assert "birth" not in prompt_text.lower()
    assert "name" not in prompt_text.lower()


def test_network_failure_returns_none_not_raises(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CLAUDE_API_KEY", "fake-key")

    def failing_post_json(url, headers, payload):
        raise ConnectionError("network down")

    monkeypatch.setattr(ai_writer, "_post_json", failing_post_json)

    result = ai_writer.rewrite_summary("career", "favourable", 5, ["fact"], "en")
    assert result is None


def test_classify_topic_returns_the_ai_pick(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CLAUDE_API_KEY", "fake-key")

    def fake_post_json(url, headers, payload):
        return {"content": [{"text": "marriage"}]}

    monkeypatch.setattr(ai_writer, "_post_json", fake_post_json)

    result = ai_writer.classify_topic("how's my love life looking", ["career", "marriage", "money"])
    assert result == "marriage"


def test_classify_topic_rejects_a_reply_outside_the_given_list(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "claude")
    monkeypatch.setenv("CLAUDE_API_KEY", "fake-key")

    def fake_post_json(url, headers, payload):
        # A hallucinated or off-menu answer must never be trusted as a topic.
        return {"content": [{"text": "astrology"}]}

    monkeypatch.setattr(ai_writer, "_post_json", fake_post_json)

    result = ai_writer.classify_topic("blah blah", ["career", "marriage", "money"])
    assert result is None


def test_classify_topic_returns_none_when_ai_is_off(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "none")
    result = ai_writer.classify_topic("how's my love life looking", ["career", "marriage"])
    assert result is None
