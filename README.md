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

## Current status: Phase 0 complete

Repo structure, Docker Compose, CI, and a health-check endpoint are in place.
See CLAUDE.md §7 for what's next (Phase 1: the Kundli engine).
