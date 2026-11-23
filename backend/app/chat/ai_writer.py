"""Optional AI rewrite (CLAUDE.md 5.3 step 6, principle 1 and 4).

Only ever sends chart facts and rule-result sentences -- never the user's
name, raw birth date/time/place, or any other personal data (principle 4:
"never send names or birth details to an AI provider"). The AI is only
asked to rephrase already-computed, already-correct facts into flowing
language; it is explicitly instructed not to add anything, and its output
is never trusted blindly -- `verifier.py` checks it afterwards, and this
function itself returns `None` (triggering the template fallback) on any
error, timeout, or missing API key, per "If AI is off or fails, templates
write the answer."
"""

import httpx

from app.config import get_settings

_TIMEOUT_SECONDS = 20
_MAX_OUTPUT_TOKENS = 400

_LANGUAGE_NAME = {"en": "English", "hi": "Hindi (Devanagari script)", "hinglish": "Hinglish"}


def _build_prompt(
    topic: str, verdict: str, score: int, rule_effects: list[str], language: str
) -> str:
    language_name = _LANGUAGE_NAME.get(language, "English")
    facts = "\n".join(f"- {effect}" for effect in rule_effects)
    return (
        f"Rewrite the following astrology reading facts as one warm, natural-sounding "
        f"paragraph in {language_name}, for a chat app. Topic: {topic}. Overall verdict: "
        f"{verdict} (score {score}).\n\nFacts (do not add, remove, or change any of these; "
        f"only rephrase them together naturally):\n{facts}\n\n"
        f"Do not invent any new facts, planets, houses, or dates. Reply with only the "
        f"rewritten paragraph, nothing else."
    )


def _post_json(url: str, headers: dict, payload: dict) -> dict:
    """Thin wrapper so tests can monkeypatch the network call."""
    response = httpx.post(url, headers=headers, json=payload, timeout=_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def _call_claude(prompt: str, api_key: str, max_tokens: int) -> str:
    data = _post_json(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        payload={
            "model": "claude-haiku-4-5",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    return data["content"][0]["text"].strip()


def _call_openai(prompt: str, api_key: str, max_tokens: int) -> str:
    data = _post_json(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
        payload={
            "model": "gpt-5-mini",
            "max_completion_tokens": max_tokens,
            # Neither rewriting nor classification benefits from extended
            # reasoning -- and without capping it, gpt-5-mini sometimes
            # spends the entire token budget on hidden reasoning tokens and
            # returns empty text (finish_reason "length") instead of a reply.
            "reasoning_effort": "minimal",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    return data["choices"][0]["message"]["content"].strip()


def _call_gemini(prompt: str, api_key: str, max_tokens: int) -> str:
    data = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        headers={"content-type": "application/json"},
        payload={"contents": [{"parts": [{"text": prompt}]}]},
    )
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


_PROVIDERS = {"claude": _call_claude, "openai": _call_openai, "gemini": _call_gemini}


def _call_configured_provider(prompt: str, max_tokens: int) -> str | None:
    """Returns the configured provider's reply, or None if AI is off,
    unconfigured, or the call failed for any reason."""
    settings = get_settings()
    provider = settings.ai_provider
    if provider not in _PROVIDERS:
        return None

    api_key = getattr(settings, f"{provider}_api_key", "")
    if not api_key:
        return None

    try:
        text = _PROVIDERS[provider](prompt, api_key, max_tokens)
    except Exception:
        return None

    return text or None


def rewrite_summary(
    topic: str, verdict: str, score: int, rule_effects: list[str], language: str
) -> str | None:
    """Returns a rewritten summary, or None if AI is off, unconfigured, or failed."""
    if not rule_effects:
        return None

    prompt = _build_prompt(topic, verdict, score, rule_effects, language)
    return _call_configured_provider(prompt, _MAX_OUTPUT_TOKENS)


_CLASSIFY_MAX_TOKENS = 20


def classify_topic(message: str, topics: list[str]) -> str | None:
    """Best-effort topic classification for messages that don't contain one
    of the fixed keywords (CLAUDE.md 5.3 step 2 is "keywords first; small
    classifier later" -- this is that classifier). The AI only ever picks
    one of the given topic names or says "none"; it never writes any part
    of the answer itself, so principle 1 ("AI only writes" rule results, via
    `rewrite_summary` above) still holds. Returns None if AI is off,
    unconfigured, failed, or didn't confidently pick a topic."""
    prompt = (
        "A user of a Vedic astrology chat app asked a question that didn't match "
        "any of our fixed keywords. Pick the single best-matching topic for it from "
        f"this exact list: {', '.join(topics)}, none.\n\n"
        f'Question: "{message}"\n\n'
        "Reply with only the one matching word from the list above, nothing else."
    )
    text = _call_configured_provider(prompt, _CLASSIFY_MAX_TOKENS)
    if text is None:
        return None

    cleaned = text.strip().strip(".").lower()
    return cleaned if cleaned in topics else None
