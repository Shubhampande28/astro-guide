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

**Important — this hasn't been accuracy-checked yet.** The chart math (ayanamsa,
planet positions, houses, dashas) needs to be checked against 10 real
reference charts before it can be trusted for real predictions. See "What I
still need from you" below.

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

## Current status: Phase 1 in progress

Phase 0 (repo structure, Docker Compose, CI) is done. Phase 1's engine code
is written and unit-tested (40 tests passing, covering ayanamsa, planet
positions, houses, nakshatra, dignity, navamsa, and Vimshottari dasha) and
the `/chart` endpoint works end-to-end.

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
