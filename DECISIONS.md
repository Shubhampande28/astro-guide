# Decisions log

Every time something in CLAUDE.md is unclear, the simplest sensible option is
picked and recorded here with the date and reason.

---

### 2026-11-23 — Python version for local venv vs. runtime
**Decision:** Pin the backend to Python 3.11 in `pyproject.toml`, the
Dockerfile, and CI, even though the machine's local Python is 3.13.
**Reason:** CLAUDE.md §5 specifies Python 3.11 for the FastAPI backend. All
real work happens inside Docker (and CI uses 3.11 explicitly), so the local
system Python version doesn't need to match. If the founder wants to run the
backend without Docker, they should install Python 3.11 separately (e.g. with
pyenv or the Microsoft Store "Python 3.11" package).

### 2026-11-23 — Package manager and lint/format tooling
**Decision:** Use `pip install -e ".[dev]"` with `pyproject.toml` (no
Poetry/uv), `ruff` for linting, `black` for formatting, `pytest` for tests.
**Reason:** Simplest standard toolchain; avoids an extra tool for the founder
to learn. Can switch to `uv` later without changing project structure.

### 2026-11-23 — `requires-python` has no upper bound
**Decision:** `requires-python = ">=3.11"` (not `>=3.11,<3.12`).
**Reason:** CLAUDE.md asks for Python 3.11 at runtime (Docker/CI pin to the
`python:3.11-slim` image and `actions/setup-python@v5` with `"3.11"`), but
pinning an upper bound in `pyproject.toml` blocked local verification on this
machine, which only has Python 3.13 installed. Docker and CI are the sources
of truth for the actual runtime version; the founder can still run the
backend locally on 3.11+ without Docker if they want to.

### 2026-11-23 — CI scope for Phase 0
**Decision:** CI only lints and tests the `backend/` folder for now (no
Android CI yet).
**Reason:** Android project doesn't exist until Phase 5. Will add a separate
CI job when Phase 5 starts.
