# Jyotish Guru

A Vedic astrology chatbot for India. See [CLAUDE.md](CLAUDE.md) for the full
product spec, principles, and build plan.

This README covers the backend only, since that's all that exists so far
(Phase 0). It will grow as the Android app and other pieces are added.

## What you need installed

- **Docker Desktop** — runs Postgres, Redis, and the backend together so you
  don't have to install any of them yourself. Download from
  https://www.docker.com/products/docker-desktop/ and make sure it's running
  (you'll see a whale icon in the system tray) before using the commands
  below.
- **Git** — to track changes. You already have this.

You do **not** need Python installed on your own machine — it runs inside
Docker.

## Running the backend

1. Open a terminal in the `jyotish-guru` folder.
2. Copy the example environment file:
   ```
   cp .env.example .env
   ```
3. Start everything:
   ```
   docker compose up
   ```
4. Wait until you see a line like `Uvicorn running on http://0.0.0.0:8000`.
5. Open http://localhost:8000/health in a browser. You should see
   `{"status":"ok","env":"development"}`.

To stop everything, press `Ctrl+C`, then run `docker compose down`.

## Trying the Kundli (birth chart) calculator

With the containers running, call the `/chart` endpoint with a birth date,
time, timezone, and location. For example (New Delhi, 15 May 1990, 8:30am):

```
curl -X POST http://localhost:8000/chart -H "Content-Type: application/json" -d "{\"birth_date\":\"1990-05-15\",\"birth_time\":\"08:30:00\",\"timezone\":\"Asia/Kolkata\",\"latitude\":28.6139,\"longitude\":77.2090}"
```

You'll get back the full chart: lagna (ascendant), all 9 grahas with their
sign/house/nakshatra/dignity, the navamsa (D9) chart, and the full
Vimshottari dasha timeline. There's no place-name search yet — you give
latitude/longitude directly (see DECISIONS.md, 2026-11-23 entry on this).

**Status: self-verified, not yet founder-verified.** I cross-checked this
engine's ayanamsa, planet positions, and ascendant against an independent
implementation (Swiss Ephemeris, used only as a one-off local test, never
part of this product — see DECISIONS.md). That caught and fixed a real bug
(the ascendant formula was silently computing the descendant) and one
calibration issue (the ayanamsa formula). For modern dates, this engine now
matches that independent implementation to within a few arcseconds —
comfortably inside CLAUDE.md's accuracy targets.

The one open question: for a 1943 test case, the ascendant differed from
the independent check by about 4 arcminutes (over the 2' target), traced to
historical uncertainty in Earth's rotation rate (delta-T) — both
implementations make a different, defensible choice there, and only a real
reference chart can say which one actually matches what Drik
Panchang/Jagannatha Hora produce. That's what the 10 reference charts below
are for.

**2026-11-23: the founder opted to skip gathering the 10 reference charts
for now** (no browser-automation tool was available in this session to
fetch them automatically, and doing it by hand was deprioritized). Phase 1
proceeds on the strength of the self-verification above. The pre-1955
ascendant precision question remains open — worth revisiting before this
engine is used for real predictions involving pre-1955 births.

## Trying the chat pipeline

With the containers running, open **http://localhost:8000/docs**, find
**POST /chat**, click "Try it out", and send a message plus birth details:

```json
{
  "message": "How is my career looking?",
  "language": "en",
  "birth_date": "1990-05-15",
  "birth_time": "08:30:00",
  "timezone": "Asia/Kolkata",
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

`language` can be `en`, `hi`, or `hinglish`. You'll get back the full
6-part answer card: topic, summary, why (matched rules), sources, timing,
remedies, and confidence. Try a distress message (e.g. "I want to kill
myself") and you'll see it short-circuits to the Tele-MANAS helpline
instead of running a reading — try a restricted one too (e.g. "when will I
die?") and you'll see it's politely declined instead of treated as a
crisis.

The AI rewrite step is off by default (`AI_PROVIDER=none` in `.env`) —
answers come from the templates. If you later get a Claude/OpenAI/Gemini
API key, set `AI_PROVIDER` and the matching `*_API_KEY` in `.env` and
restart; if anything about that call fails, it silently falls back to the
template, so it's safe to try.

## Trying the rules engine

The rules engine takes a chart plus a topic ("career", "marriage", "money",
"health", "education", "foreign_travel", "children", "property") and
returns which rules matched, a score, a verdict, and when (which dasha
periods) the topic is most active. There are 200 seed rules (25 per topic),
all currently `status: draft` — no astrologer has reviewed them yet (that's
Phase 9's admin panel), so this is a demonstration of the engine, not
vetted predictions.

To see it work end-to-end for 3 example births (modern, 1943 wartime IST,
and southern-hemisphere):

```
docker compose exec backend python -m scripts.sample_rules_report
```

This prints, for each birth and each topic, the matched rules with their
weights, the overall score/verdict, and the dasha timing window.

## Running the tests

With the containers running (in another terminal):

```
docker compose exec backend pytest
```

You should see all tests pass (green). This is what CI also runs
automatically on every push to GitHub.

## Checking code style

```
docker compose exec backend ruff check .
docker compose exec backend black --check .
```

## Project layout

```
jyotish-guru/
  CLAUDE.md       Full product spec and build plan — read this first
  DECISIONS.md    Log of judgment calls made and why
  LICENSES.md     Every dependency's licence (must stay MIT/Apache/BSD, never AGPL/GPL)
  docker-compose.yml   Starts Postgres, Redis, and the backend together
  .env.example    Template for secrets/config — copy to .env, never commit .env
  backend/        FastAPI backend (Python)
    app/
      astro/      Kundli (birth chart) calculation engine
      rules/      YAML astrology rules + the code that evaluates them
      chat/       Chat pipeline: safety check, intent detection, answers
      palm/       Palm-reading image pipeline
      match/      Kundli matching for marriage (Ashtakoota)
      payments/   Razorpay integration
      admin/      Astrologer rule-review panel
    tests/        Automated tests
    rules_data/   The actual YAML rule files (added in Phase 2)
  android/        Android app (added in Phase 5)
  docs/           API reference and rule-writing guide
```

## Current status: Phase 3 in progress

Phase 0 (repo structure, Docker Compose, CI) is done. Phase 1's Kundli
engine is built, unit-tested, and self-verified against an independent
implementation (one open item remains: pre-1955 ascendant precision — see
below). Phase 2's rules engine (safe condition DSL, evaluator, 200 seed
rules) is done. Phase 3's chat pipeline is built: safety check, topic +
timeframe detection in English/Hindi/Hinglish, the 6-part answer card,
optional AI rewrite with a verifier guard against hallucination, and the
`/chat` endpoint — all unit-tested (120 tests passing across all three
phases). The required 50-question benchmark scores **100% topic accuracy
and 0 safety failures** (target was ≥90% / 0).

### What I still need from you to finish Phase 1

CLAUDE.md's accuracy gate for Phase 1 requires checking this engine against
**10 real reference charts** before it's considered done — I can't generate
these myself; they need to come from a real astrology tool so we have ground
truth to compare against:

1. Pick 10 people (can be public figures, family, or made-up test cases) with
   known birth date, time, and place.
2. Look each one up on **Drik Panchang** (drikpanchang.com) or in
   **Jagannatha Hora** (free desktop software) and note down: each planet's
   sign and degree, the ascendant (lagna), and the current Vimshottari
   maha/antar dasha.
3. Include at least: one birth from 1943 or earlier, one from before 1955,
   and one from the southern hemisphere (CLAUDE.md is specific about these
   edge cases, since timezone history and sign math behave differently
   there).
4. Send me the 10 sets of birth details + what Drik Panchang/Jagannatha Hora
   said for each.

I'll run the same 10 births through this engine and compare. If the ayanamsa
or ascendant comes out systematically off by a fixed amount, I can tune a
calibration constant already built in for exactly that (see DECISIONS.md).

### What to review for Phase 2

The 200 seed rules are generated from a template (see `scripts/
generate_seed_rules.py` and the DECISIONS.md entry on this) — the
*mechanism* (house placement, dignity, aspects, conjunctions, dasha) is
classically grounded, but no astrologer has reviewed the actual rule text
or weights yet. Run the sample report above and skim a topic or two; if
anything reads wrong astrologically, that's exactly the kind of feedback
the admin panel (Phase 9) is meant to collect — for now, just tell me and
I'll adjust the generator or the rule content directly.

### What to review for Phase 3 — important

`app/chat/safety.py`'s self-harm/distress phrase lists are my first pass,
**not a clinically validated classifier**. They pass the 50-question test
set with zero failures, but that test set is also something I wrote, not
a mental-health professional. Before this app is used by real people, I'd
strongly recommend having someone with crisis-response experience review
and expand that keyword list — this is the one piece of the whole system
where a gap has real consequences.
