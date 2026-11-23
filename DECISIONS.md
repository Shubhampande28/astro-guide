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

### 2026-11-23 — Condition DSL uses Python's `ast`, not a hand-written parser
**Decision:** `app/rules/dsl.py` parses conditions with `ast.parse(mode="eval")`
(builds a syntax tree only, never calls `eval`/`exec`), then validates the
tree against a strict node/function/attribute whitelist before walking it
with our own interpreter.
**Reason:** CLAUDE.md 5.2 asks for a safe DSL with exactly the syntax Python
expressions already have (`lord(10) in house(11)`, `and`/`or`/`not`,
`==`/`!=`). Reusing Python's own parser for the *syntax* only, while fully
owning what each node means and rejecting anything not on the whitelist
(imports, lambdas, arbitrary calls, `__class__`, chained comparisons,
etc.), is simpler and better-tested than writing a tokenizer/parser from
scratch, and is still exploit-proof since no Python code is ever executed.

### 2026-11-23 — Remedies catalog deferred
**Decision:** Every seed rule has `remedies: []`.
**Reason:** CLAUDE.md's rule format references remedy IDs (e.g.
`REM-SUN-01`), but building that catalog is out of scope for "rules engine
+ 200 seed rules" (Phase 2's actual deliverable). Will add remedy IDs once
a remedies catalog exists, likely alongside the chat pipeline (Phase 3) or
when the founder specifies which remedies to offer (principle 3: no
expensive remedy pushing).

### 2026-11-23 — The 200 seed rules are template-generated, not hand-written
**Decision:** `scripts/generate_seed_rules.py` produces all 200 rules from
one 25-slot template per topic (house-lord placement across all 12 houses,
the topic's classical karaka's dignity, a secondary karaka's dignity,
retrograde, aspects from Jupiter/Saturn, conjunction with Jupiter/Saturn,
and dasha activation), with the house/karaka choices per topic set by hand
in that script.
**Reason:** Hand-writing 200 individually distinct rules wasn't a good use
of time versus encoding the underlying classical pattern once and
generating consistent, DSL-valid, non-duplicated output. All 200 are
seeded as `status: draft` specifically so the founder (an astrologer) can
review, edit, or reject them via the admin panel in Phase 9 -- generated
is not the same as pre-approved. A general house-strength table (trikona
1/5/9 and kendra 4/7/10 strongest, upachaya 3/6/11 supportive, dusthana
6/8/12 challenging) is reused across all 8 topics rather than writing a
bespoke weighting per topic, which is a simplification worth revisiting
once real rules get astrologer review.

### 2026-11-23 — Graha drishti (aspect) and conjunction definitions
**Decision:** `aspects(X, n)`: every graha aspects the 7th house from
itself; Mars/Jupiter/Saturn additionally aspect 4th&8th / 5th&9th / 3rd&10th
respectively (Parashari); Rahu/Ketu get only the standard 7th aspect.
`conj(X, Y)`: true when X and Y occupy the same sign (rashi), not
necessarily the same house-relative-to-lagna (they're the same thing for a
natal chart, but this matters once transit charts are involved).
**Reason:** Classical texts disagree on whether Rahu/Ketu get Mars/Saturn-
style special aspects; the conservative reading (no) avoids silently
picking a tradition the founder hasn't chosen. Same-sign conjunction is the
standard definition across traditions.

### 2026-11-23 — Chat pipeline: Phase 3 scope excludes persistence
**Decision:** `handle_message()` takes the chart and rule list as plain
arguments; it does not fetch from a cache, a database, or save history.
**Reason:** CLAUDE.md 5.3 lists "chart from cache" (step 3) and "save"
(step 8) as part of the pipeline, but profiles/history/DB persistence are
explicitly Phase 4's scope ("API, auth, profiles, history, feedback,
DPDP"). The `/chat` endpoint computes the chart fresh per request for now;
wiring in Redis caching and Postgres history save/retrieve happens in
Phase 4 without changing this module's interface.

### 2026-11-23 — Restricted topics are declined, not treated as a crisis
**Decision:** Death/accident timing, medical diagnosis, legal, and
stock-trading questions are detected by `intent.py` as their own
pseudo-topics and get a short decline message (`templates.build_declined`).
Only actual distress/self-harm language triggers the Tele-MANAS crisis
response in `safety.py`.
**Reason:** CLAUDE.md principle 3 lists these as two different things --
"no death/accident timing, no medical diagnosis..." is a content policy,
while "distress or self-harm words -> stop the reading... Tele-MANAS" is a
crisis protocol. Treating "when will I die?" as a mental-health crisis
would be both wrong and could feel alarming to someone asking an ordinary
(if off-limits) astrology question.

### 2026-11-23 — Safety keyword lists are a first pass, not clinical
**Decision:** `safety.py`'s distress-phrase lists are hand-written,
favouring false positives (an unnecessary but harmless care message) over
false negatives (a missed crisis).
**Reason:** This is safety-critical and keyword matching is a blunt tool.
The 50-question test set (`tests/chat/fifty_question_test_set.py`) currently
passes with 0 failures, but that test set is not exhaustive. Recommend a
mental-health professional or crisis-response specialist review this list
before real users rely on it, and that it be revisited whenever a real
conversation reveals a phrase it missed.

### 2026-11-23 — AI rewrite only ever touches `summary`, never Why/Sources/Timing
**Decision:** `ai_writer.rewrite_summary()` returns a single rewritten
paragraph that replaces `AnswerCard.summary` display (stored separately as
`ai_rewritten_summary`, template `summary` kept as fallback); Why, Sources,
Timing, and Remedies are always the literal template text, never passed
through the AI.
**Reason:** Principle 1 ("AI only writes... may not add any fact") is
easiest to guarantee by construction: the facts (Why/Sources/Timing/
Remedies) are never generated by the AI at all, so there's nothing there
for it to hallucinate. Only the conversational framing sentence is ever at
risk, and that's exactly what `verifier.py` checks before use.

### 2026-11-23 — Tables created via `create_all`, not Alembic migrations yet
**Decision:** `app/db.py`/`app/main.py` create tables with
`Base.metadata.create_all` at startup, even though Alembic is already a
declared dependency.
**Reason:** The Phase 4 schema (users/profiles/chat_messages/feedback/
otp_codes) is brand new and likely to shift as Phase 5 (Android) surfaces
real requirements. Writing migrations for a schema that's still moving is
more overhead than value right now. Switch to real Alembic migrations once
the schema survives contact with the Android app without changing, so a
production upgrade never risks a hand-edited `ALTER TABLE`.

**2026-11-23, observed consequence:** adding `User.is_guest` (for the
skip-sign-in flow, see the guest-login entry below) hit exactly the risk
this decision names: the existing dev Postgres volume already had a
`users` table from before the column existed, `create_all` doesn't alter
existing tables, and every insert into `users` failed with `column
"is_guest" of relation "users" does not exist` until the dev volume was
dropped and recreated (`docker compose down -v`). Fine for local dev data;
would not be fine for anything with real users in it -- another reason to
move to real migrations before this schema reaches production.

### 2026-11-23 — Phone OTP has no real SMS gateway yet
**Decision:** `app/accounts/otp.py`'s `send_otp()` just logs the code
(dev-only); the request/verify/JWT flow is real, only the delivery
mechanism is stubbed.
**Reason:** CLAUDE.md doesn't name an SMS provider, and picking one (e.g.
MSG91, commonly used for Indian OTP) needs the founder's account/API key
regardless. The interface is isolated to this one function, so swapping in
a real provider later doesn't touch auth logic, the DB schema, or any
caller.

### 2026-11-23 — Sign-in is optional: a guest account with no phone number
**Decision:** Added `POST /auth/guest` (`app/accounts/router.py`), which
creates a `User` with `is_guest=True` and a synthetic `phone_number` (e.g.
`guest:a1b2c3...`) -- no phone number is ever collected -- and returns a
JWT exactly like OTP verification does. The Android app's first screen now
offers "Sign in with phone" or "Skip for now"; skipping calls this
endpoint and proceeds straight to consent -> onboarding -> chat.
**Reason:** Founder feedback: requiring a phone number before someone can
even try the app is unnecessary friction for a user who "thinks this is
not important" and just wants to ask a question. Everything downstream
(consent, profile encryption, history, delete-my-data) works identically
for a guest account; only the login method and the absence of a phone
number differ. A guest can still sign in with a phone number later from
the menu -- that's a separate, not-yet-built step (currently "Sign in"
from Home always starts a *new* phone login rather than *upgrading* the
current guest session to one; linking the two is future work once there's
a reason to, e.g. before Phase 8 payments).

### 2026-11-23 — Birth place: a real offline India dataset, not raw lat/lon
**Decision:** Onboarding no longer asks for latitude/longitude at all.
Birth place is selected as **State -> District -> City/Town** for India
(`IndiaPlacesRepository`, backed by `app/src/main/assets/india_places.json`,
7,324 real places across all 36 states/UTs, generated from GeoNames'
`cities500` export + `admin1`/`admin2` code files by
`android/scripts/build_india_places.py`), or a short fallback list
(`InternationalPlaces.kt`) for births outside India. Latitude/longitude/
timezone are looked up from the selected place and sent to the backend
without ever being shown to the user.
**Reason:** Founder feedback: "no one knows the latitude and longitude" --
asking for them was never reasonable to expect from a non-technical user,
and this is exactly the "offline GeoNames... database" CLAUDE.md 5.1
already specified for place search (previously deferred for Phase 1's
narrower scope: the chart math itself). Also addressed directly: "atleast
india you should know all places" (comprehensive India coverage, not a
hand-picked list of ~40 cities) and "ask for state and district as well so
as more accuracy is found" (disambiguates same-named towns in different
states/districts, and narrows a long list to a manageable one at each
step). The raw GeoNames text dumps (~44MB) are not committed -- only the
generated `india_places.json` (646KB) is; the generator script documents
how to re-fetch the inputs if the dataset needs updating.

### 2026-11-23 — "Myself" vs "a family member", and reusing a returning user's own profile
**Decision:** Onboarding now opens by asking "Whose Kundli is this? Myself
/ A family member" (`relation: "self" | "family"`, already part of the
Phase 4 data model, just not surfaced as an explicit choice before).
Separately, `SplashGate` (`ui/nav/AppNav.kt`) now explicitly prefers the
profile with `relation == "self"` as the active profile when a returning
user's profile list is non-empty, rather than just whichever profile
happens to be first in the list.
**Reason:** Founder feedback: "if they sign in they fetch that info from
there if its for them... if someone else then they can enter manually."
A phone account that already has a profile already skips onboarding
entirely on a later sign-in (profiles are looked up by phone number, and
an empty list is the only thing that routes to onboarding) -- that part
already worked. What was missing was making the self/family choice
explicit in the UI (it was silently hardcoded to `"self"` before) and
making sure *which* profile gets reused on return is deliberately the
user's own, not just the first one created.

### 2026-11-23 — What's encrypted at rest and what isn't
**Decision:** `Profile.birth_date/birth_time/latitude/longitude` and
`ChatMessage.message_text/summary` are Fernet-encrypted; `Profile.name`
and `topic`/`language`/`confidence` are plain text.
**Reason:** CLAUDE.md principle 4 specifically calls out encrypting birth
data; chat content can reveal sensitive topics (health, relationships) so
it's encrypted too, by the same reasoning. Name is needed in the clear for
profile-switching UI (F8) and isn't itself astrologically identifying the
way a birth date/time/place triple is.

### 2026-11-23 — `/chat` now requires a saved profile, not raw birth fields
**Decision:** Phase 3's `/chat` took birth date/time/place directly in the
request body; Phase 4 changes it to take a `profile_id` (auth required)
and look the birth data up from the encrypted profile.
**Reason:** This is the real shape the product needs once profiles exist
-- a user shouldn't have to resend their birth details with every chat
message. All Phase 3 tests were updated to the new shape rather than kept
side by side with a legacy endpoint, since CLAUDE.md doesn't ask for
backwards compatibility with a pre-auth API that was never released.

### 2026-11-23 — Unknown birth time defaults to local noon (placeholder)
**Decision:** A profile with `birth_time_unknown=true` and no birth time
computes its chart at 12:00 local time.
**Reason:** F6's real behavior (Moon-sign-only analysis, lower confidence,
offer Prashna/horary) isn't built yet -- that's a meaningful chunk of work
on its own. Noon is a common convention for "unknown time" charts and lets
the rest of the pipeline run without crashing; `birth_time_unknown` is
still stored so F6 can be implemented properly later without a data
migration.

### 2026-11-23 — Android build toolchain: using Android Studio's bundled JDK/SDK directly
**Decision:** The Android project builds with Gradle 8.14.3 (already cached
locally), Android Gradle Plugin 8.5.2, and Kotlin 1.9.24, using the JDK and
SDK that ship inside the Android Studio install on this machine (no
separate JDK/SDK install), referenced via `JAVA_HOME`/`ANDROID_HOME`/
`local.properties`.
**Reason:** This machine had no standalone Java/Gradle/Android SDK, but
already had Android Studio installed with everything needed bundled
inside it, plus a working emulator AVD. Two Windows-specific gotchas
along the way, now avoided: (1) `JAVA_HOME` containing a space ("Program
Files") breaks some native process launches -- use the short path form
(`C:\PROGRA~1\...`) instead; (2) `local.properties`'s `sdk.dir` is parsed
as a Java `.properties` file, where `\` is an escape character -- use
forward slashes (`C:/Users/...`) instead of backslashes, or the path
silently corrupts.

### 2026-11-23 — Onboarding uses plain text fields for date/time/location
**Decision:** Birth date and time are typed as `YYYY-MM-DD` / `HH:MM` text
rather than native Android date/time picker dialogs; birth place is
latitude/longitude text fields rather than a place-name search.
**Reason:** Matches the backend's existing scope decisions (no place-name
geocoding yet, see the Phase 1 DECISIONS.md entry) and ships a working
onboarding flow fast. Native pickers and place autocomplete are
straightforward additions later and don't change the API contract, so
deferring them doesn't create rework risk.

### 2026-11-23 — No ViewModel layer; screens hold their own state
**Decision:** Compose screens use `remember { mutableStateOf(...) }` and
`rememberCoroutineScope()` directly, with a thin `AppContainer`
(`JyotishGuruApp`) providing the shared `ApiService`/`TokenStore`, rather
than a ViewModel per screen.
**Reason:** State does not need to survive process death for this MVP
(whoever's asking a question again after a config change can just re-ask),
and this keeps the codebase small and easy to follow for a founder who
isn't a developer. Worth revisiting (real ViewModels + state restoration)
once the app has paying users and losing in-progress chat input to a
rotation becomes a real complaint.

### 2026-11-23 — Self-verified on a real emulator, not just "it compiles"
**Decision:** Beyond a successful Gradle build, the app was installed on
the project's existing Android emulator (AVD `Medium_Phone_API_36.0`) and
driven end-to-end via `adb`: OTP login, consent, profile creation, a real
chat exchange against the live rules engine, the expandable answer card,
the profile/language menu, and the Kundli view -- each step screenshotted
and visually confirmed, the same standard used for the backend's Docker
verification.
**Reason:** "Builds successfully" and "works" are different claims; this
project's working rules call for tests/verification before calling
something done, and a UI is not meaningfully verified by its build log
alone.

### 2026-11-23 — Ephemeris file is downloaded, not committed
**Decision:** The NASA JPL DE440s file (~32MB) downloads automatically into
`backend/data/` (gitignored) on first use, via Skyfield's `Loader`, instead
of being committed to the repo.
**Reason:** 32MB is too large for a git repo to carry comfortably, and it's
public NASA data anyway — no reason to version it. This does mean the very
first `/chart` call (or test run) after a fresh clone needs internet access
once; after that it's cached on disk.

### 2026-11-24 — ViewModel per screen added (supersedes the 2026-11-23 "no ViewModel layer" entry)
**Decision:** Home/Chat, Onboarding, Login and Kundli each got a
`ViewModel` exposing `StateFlow<UiState>` (a hand-rolled `viewModelFactory`
since the app has no DI framework); plain text input fields stay as
`rememberSaveable` in the composable rather than moving into the
ViewModel.
**Reason:** UI_CHANGES.md A5 (external Android design review): rotating
the phone mid-chat was losing messages and re-triggering API calls, which
is a worse failure mode than the small added structure costs. ViewModels
also give every screen a natural place to put the delete-confirmation flow
(A1) and future retry/offline logic (Group F) without threading callbacks
through the composable.

### 2026-11-24 — Token storage moved off security-crypto to DataStore + Keystore
**Decision:** `TokenStore` now AES/GCM-encrypts values with a key held in
the Android Keystore (`KeystoreCrypto`) and persists them as base64 in a
Preferences DataStore, instead of
`androidx.security:security-crypto:1.1.0-alpha06`.
**Reason:** UI_CHANGES.md A4: that library has been in alpha for years and
is unmaintained. The public `TokenStore` API stays synchronous (a
`runBlocking` read once at `Application.onCreate`, matching what
`EncryptedSharedPreferences.create(...)` already did; an in-memory cache
after that, with writes persisted asynchronously) so none of the existing
call sites — the OkHttp interceptor on a background thread, several
`LaunchedEffect`/`scope.launch` blocks on the main thread — had to change.

### 2026-11-24 — compileSdk 36 / AGP 8.13.2, not AGP 9 / compileSdk 37
**Decision:** UI_CHANGES.md A7 asked to raise compileSdk/targetSdk "to
match" Google Play's current requirement, which is API 36. compileSdk and
targetSdk were raised to 36 with AGP bumped to 8.13.2 (the latest 8.x
release supporting it) and Gradle to 8.14.3. AGP 9.x / compileSdk 37 was
deliberately not taken, even though it's the newer option, and several
AndroidX libraries (navigation-compose 2.10.x, the newest Compose BOM,
lifecycle 2.11.x) were pinned one notch below their absolute latest
because their newest releases require it.
**Reason:** AGP 9 is a major-version migration (new Gradle line, K2-only
tooling changes) that UI_CHANGES.md didn't ask for, and this sandbox
couldn't even download a newer *patch* of the existing Gradle 8.x wrapper
(network allowlist issue specific to Java's `URLConnection`, confirmed
working via `curl` to the same URL) — attempting a full AGP-9/Gradle-9
migration un-verifiable in this environment was too large a risk to take
silently. Revisit once compileSdk 37 is required or verification isn't
network-constrained.

### 2026-11-24 — Release API host is a placeholder
**Decision:** UI_CHANGES.md A2 (cleartext traffic only in debug) needed a
real `release` `API_BASE_URL`; `https://api.jyotishguru.app/` was used as
a placeholder since no production host exists yet.
**Reason:** A domain this project doesn't control shouldn't be invented
silently without the founder's sign-off. Flagged with a `TODO(DECISIONS.md
A2)` comment at the `release` build type in `app/build.gradle.kts` --
replace before any release build is actually shipped.
