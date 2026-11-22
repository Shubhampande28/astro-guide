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

### 2026-11-23 — Lahiri ayanamsa computed from Spica, not a fixed table
**Decision:** Ayanamsa = tropical longitude of the star Spica (via Skyfield,
full precession/nutation/aberration) minus 180 degrees, with a
`CALIBRATION_OFFSET_DEG` constant (currently 0) in `app/astro/ayanamsa.py`.
**Reason:** This is the literal definition of "Chitrapaksha" that CLAUDE.md
names — Spica (Chitra) anchored at 180 degrees. Published Lahiri tables can
differ from a pure Spica calculation by up to roughly half an arcminute
depending on exactly which historical star coordinates/precession model the
original committee used. The accuracy gate (10 reference charts, still
needed from the founder) is what tunes `CALIBRATION_OFFSET_DEG` if the
reference software shows a consistent offset.

### 2026-11-23 — Rahu/Ketu have no classical dignity
**Decision:** `dignity()` returns `"neutral"` for Rahu and Ketu always.
**Reason:** Classical texts disagree on which signs the lunar nodes are
exalted/debilitated in (Gemini/Sagittarius vs. Taurus/Scorpio are both
cited). Guessing one risks silently baking in a tradition the founder (an
astrologer) didn't choose. Revisit once they pick one.

### 2026-11-23 — `/chart` takes latitude/longitude directly, not a place name
**Decision:** Phase 1's `/chart` endpoint requires the caller to already have
latitude, longitude, and an IANA timezone name — it does not do place-name
geocoding.
**Reason:** CLAUDE.md 5.1 specifies an offline GeoNames cities500 lookup for
place search, but that's really part of F1 (onboarding, place autocomplete)
rather than the chart math itself. Phase 1's "done when" criterion is the
accuracy gate on 10 reference charts, which doesn't need geocoding. Add
geocoding when F1/the Android onboarding flow is built, or sooner if asked.

### 2026-11-23 — `tzdata` added as an explicit dependency
**Decision:** Added the `tzdata` PyPI package (Apache-2.0/MIT) rather than
relying on the OS having IANA timezone data installed.
**Reason:** Windows does not ship IANA tz data at all, and some minimal
Linux/Docker base images don't either. Without it, every `zoneinfo.ZoneInfo`
lookup (including the historical Asia/Kolkata offset handling this product
depends on) fails outright. Confirmed locally: `ZoneInfo("Asia/Kolkata")`
raised `ZoneInfoNotFoundError` on this Windows machine until `tzdata` was
installed.

### 2026-11-23 — Self-verified the engine against Swiss Ephemeris (never shipped)
**Decision:** Before asking the founder for the 10 reference charts, I
installed `pyswisseph` (GPL) into a throwaway venv in the scratchpad
directory — never added to `pyproject.toml`, never committed, never run in
Docker — purely to cross-check this engine's numbers against a second,
independent, widely-trusted implementation.
**Reason:** CLAUDE.md forbids pyswisseph/AGPL/GPL libraries *in the
product*, which this respects (it never touched the repo or a real
dependency file). Using it as a local, disposable test oracle is a
different thing from shipping it, and it caught two real issues before the
founder ever had to look at a single chart:

1. **A real bug, fixed**: `ascendant.py`'s formula had both `atan2` argument
   signs flipped, which silently computed the *descendant* instead of the
   ascendant (exactly 180 deg off) in every chart. Caught by comparing a
   1990 New Delhi chart's ascendant to Swiss Ephemeris's `houses_ex()`,
   which immediately showed a ~180 deg gap. Fixed; now matches Swiss
   Ephemeris's modern-date ascendant to ~9-19 arcsec.
2. **Not a bug, a calibration fact**: the first version of `ayanamsa.py`
   computed the ayanamsa from Spica's literal tropical position (true
   "Chitrapaksha"). That differs from the ayanamsa Indian software/Drik
   Panchang/Jagannatha Hora actually use ("Lahiri", Swiss Ephemeris's
   `SIDM_LAHIRI`) by about 1-1.5 arcmin — too large for the ≤10" ayanamsa
   accuracy gate. Replaced it with the IAU 2006 precession-in-longitude
   formula anchored at 85885.53" at J2000.0 (a published astronomical
   constant, not GPL code), which now matches Swiss Ephemeris's Lahiri mode
   to better than 0.01 arcsec from 1900 to 2100.

**What this does and doesn't cover**: modern-date (post-1972) planet
positions, ayanamsa, and ascendant all now match Swiss Ephemeris to a few
arcsec/arcmin — comfortably inside every accuracy-gate tolerance in CLAUDE.md
5.1. For the pre-1955 case specifically, cross-checking a 1943 Bombay chart
showed the ascendant differing from Swiss Ephemeris by ~4.4 arcmin (over the
2' tolerance), traced to Skyfield and Swiss Ephemeris using different
historical delta-T (Earth rotation) reconstructions for that era — sidereal
time itself differed by ~4 arcmin, which planet positions aren't as
sensitive to, but the ascendant is. This is a genuine, known source of
uncertainty for pre-1955 dates (Earth's historical rotation isn't perfectly
known), not a bug in either implementation, and it's exactly why CLAUDE.md
asks for a real pre-1955 reference chart: whichever delta-T table Drik
Panchang/Jagannatha Hora uses is the one this product needs to match, and
that can only be confirmed against real reference data, not another
independent calculation.

### 2026-11-23 — Ephemeris file is downloaded, not committed
**Decision:** The NASA JPL DE440s file (~32MB) downloads automatically into
`backend/data/` (gitignored) on first use, via Skyfield's `Loader`, instead
of being committed to the repo.
**Reason:** 32MB is too large for a git repo to carry comfortably, and it's
public NASA data anyway — no reason to version it. This does mean the very
first `/chart` call (or test run) after a fresh clone needs internet access
once; after that it's cached on disk.
