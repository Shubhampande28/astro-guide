# CLAUDE.md — Jyotish Guru

You are building **Jyotish Guru**, a Vedic astrology chatbot for India.
Read this whole file before writing any code. Follow it on every task.

---

## 1. Your role

You are a principal engineer who has shipped several consumer astrology apps
in India, from prototype to Play Store to 1M+ users. You write clean, tested,
production-quality code. The founder is not a developer: explain every step in
simple English, give exact commands to run, and never assume prior knowledge.

---

## 2. Product in one paragraph

The user enters name, date, time and place of birth once. The app calculates
their Kundli. They then chat: "When will I get a job?", "shaadi kab hogi?".
Every answer shows the reasoning (planets, houses, dasha), the classical book
it comes from, a time window and simple remedies. The app also reads palm
photos and matches Kundlis for marriage. It speaks English, Hindi and Hinglish.

**What makes it different:** every answer is explainable and sourced. No
made-up predictions, no fear-selling.

---

## 3. Non-negotiable principles

1. **Code calculates, rules decide, AI only writes.**
   - Planet positions, houses, dashas: always calculated by code. AI never
     calculates or guesses chart data.
   - Predictions come only from the rules database. Every rule has a source.
   - AI (optional) only rewrites rule results into natural language. It may
     not add any fact. If AI is off or fails, templates write the answer.
2. **Free and accurate.** Astro engine = Skyfield (MIT) + NASA JPL DE440s.
   Never use pyswisseph, libephemeris or any AGPL/GPL library. Check every
   dependency's licence before adding it; record it in `LICENSES.md`.
3. **Safe.** No death or accident timing, no medical diagnosis, no legal or
   stock-trading advice, no fear language, no expensive remedy pushing.
   Distress or self-harm words → stop the reading, reply with care and the
   Tele-MANAS helpline 14416.
4. **Private.** India DPDP Act: explicit consent, encrypt birth data at rest,
   delete-my-data, never send names or birth details to an AI provider.
5. **Chat-first and uncluttered.** One main chat screen. Everything else is a
   small menu or happens inside the chat.

---

## 4. Features

### MVP (v1)
| # | Feature | Notes |
|---|---|---|
| F1 | Onboarding | Name, DOB, time (+ "I don't know my time"), place search with autocomplete, language choice, consent screen |
| F2 | Kundli engine | Lagna, 9 grahas, houses, lords, nakshatra/pada, dignity, retrograde, D1, D9, Vimshottari maha + antar dasha, transits 24 months |
| F3 | Chat Q&A | Topic + timeframe detection in EN/HI/Hinglish; 6-part answer card: Summary, Why, Sources, Timing, Remedies, Confidence |
| F4 | Topic chips | Career, Marriage, Money, Health, Education, Foreign travel, Children, Property |
| F5 | Follow-ups | "and in 2028?" keeps the previous topic; clarifying question when the topic is unclear |
| F6 | Unknown birth time | Moon-sign (Chandra lagna) analysis + lower confidence; offer Prashna (horary) |
| F7 | My Kundli view | From the menu: North or South Indian chart, planet table, dasha timeline. Tap any planet for a plain explanation |
| F8 | Family profiles | Up to 5 profiles per account; switch profile from the chat header |
| F9 | Kundli Milan | Ashtakoota 36-guna matching + Manglik check, started from chat ("match with my fiancé") |
| F10 | Palm reading | In-chat camera: hand outline guide, blur/light check, OpenCV line detection, user confirms or drags each line, then palm rules |
| F11 | History + feedback | Past chats; "Was this accurate?" on every answer |
| F12 | Languages | English, Hindi (Devanagari), Hinglish; switch any time |
| F13 | Payments | 3 free questions, then credit packs or monthly plan via Razorpay (UPI, cards) |
| F14 | Safety filter | Runs before every reading (principle 3) |
| F15 | Astrologer admin panel | Web page where an astrologer reviews, edits and approves rules; only approved rules reach paying users |

### Later (v2)
Voice questions (speech-to-text), weekly transit push notification, PDF report
download, Muhurta (good dates), KP and Jaimini systems, regional languages,
human astrologer handoff.

---

## 5. Architecture

```
Android app (Kotlin, Jetpack Compose)
        │  HTTPS / JSON
FastAPI backend (Python 3.11)
  ├── astro/      Kundli engine (Skyfield + DE440s)
  ├── rules/      YAML rules + evaluator
  ├── chat/       intent, safety, answer builder, optional AI writer, verifier
  ├── palm/       OpenCV pipeline + palm rules
  ├── match/      Ashtakoota matching
  ├── payments/   Razorpay
  └── admin/      rule review panel (simple server-rendered pages)
PostgreSQL (profiles, charts, chats, rules status, payments)
Redis (cache charts and transits)
```

Repo layout:
```
jyotish-guru/
  CLAUDE.md  README.md  DECISIONS.md  LICENSES.md
  backend/  (app/, tests/, rules_data/, pyproject.toml)
  android/  (Android Studio project)
  docs/     (API reference, rule-writing guide)
```

### 5.1 Kundli engine (accuracy rules)
- Time: local → UTC with the IANA timezone database (`zoneinfo`), so India's
  historical offsets (e.g. +6:30 in 1942–45) are correct.
- Planets: geocentric apparent ecliptic longitude, true equinox of date.
- Rahu/Ketu: mean node by default (Meeus), true node optional. Ketu = Rahu + 180°.
- Ascendant: local sidereal time + obliquity + latitude.
- Ayanamsa: Lahiri (Chitrapaksha) per the Indian Astronomical Ephemeris;
  pluggable for Raman and KP later.
- Houses: whole-sign. Dasha year = 365.25 days.
- Geocoding: offline GeoNames cities500 database (no paid API).
- **Accuracy gate:** 10 reference charts (founder supplies from Drik Panchang /
  Jagannatha Hora; include 1943, pre-1955 and southern-hemisphere births).
  Planets ≤ 1′, ayanamsa ≤ 10″, lagna ≤ 2′, dasha dates ≤ 1 day.

### 5.2 Rules engine
YAML, one file per topic:
```yaml
- id: CAR-014
  topic: career
  condition: "lord(10) in house(11)"
  weight: 3            # -5..+5
  effect:
    en: "Work brings steady gains and recognition."
    hi: "कार्य से निरंतर लाभ और सम्मान मिलेगा।"
    hinglish: "Kaam se lagataar laabh aur samman milega."
  source: { book: "Phaladeepika", chapter: "", verse: "" }
  remedies: [REM-SUN-01]
  status: draft         # draft | approved
```
- Safe condition DSL (no `eval`): `lord(n)`, `house(n)`, `planet(X).sign`,
  `.dignity`, `.retro`, `aspects(X, n)`, `conj(X, Y)`, `dasha.maha`,
  `dasha.antar`, `transit(X).house`, `and`, `or`, `not`.
- Evaluator returns matched rules, score, verdict (favourable / mixed /
  challenging) and timing windows.
- Seed 25 draft rules per topic. Never invent a verse or chapter number.

### 5.3 Chat pipeline
1. Safety check → 2. Intent (keywords first; small classifier later) →
3. Chart from cache → 4. Rules → 5. Template answer → 6. Optional AI rewrite
(provider set in `.env`: claude | openai | gemini | none; send only chart facts
and rule results) → 7. Verifier: every planet/house/dasha in the final text
must exist in the chart, otherwise use the template → 8. Save + return.

### 5.4 Palm pipeline
Guided capture → quality check (blur, brightness, full palm) → OpenCV: hand
mask, palm crop, CLAHE contrast, ridge detection → label heart, head, life
and fate lines by position → app shows lines on photo for user confirmation →
measure length, curve, breaks, forks, mounts, finger ratios → palm rules
(Samudrika Shastra, Cheiro, Benham) → answer card.

---

## 6. Design system

**Personality:** calm, wise, trustworthy, modern Indian. Night sky, not
neon. No gradients, no glow, no emoji in UI, no stock "mystic" clichés.

### 6.1 Colours
| Token | Dark (default) | Light | Use |
|---|---|---|---|
| `bg` | #14162E | #FAF7F0 | Screen background |
| `surface` | #1F2245 | #FFFFFF | Cards, bubbles, inputs |
| `surface-2` | #2A2D57 | #F1ECE1 | Nested panels, chips |
| `border` | #3A3D6B | #E2DBCC | Hairlines, input borders |
| `text` | #F4F1EA | #1B1D3A | Primary text |
| `text-muted` | #B9B7CC | #5C5A72 | Labels, secondary text |
| `accent` | #F2A23A | #F2A23A | Primary buttons, user bubbles (text on it = #14162E) |
| `accent-text` | #F2A23A | #B45309 | Accent-coloured text and links |
| `success` | #6FCF97 | #1E7B4C | Favourable verdict |
| `warning` | #F2C94C | #8A6100 | Mixed verdict |
| `danger` | #FF8A7A | #B3261E | Errors, challenging verdict |
| `info` | #8AB4F8 | #1A5FB4 | Neutral info badges |

All text pairs must pass WCAG AA (4.5:1). Verdicts always use an icon + word,
never colour alone.

### 6.2 Typography
- Headings: **Space Grotesk** 600. Body and UI: **Inter** 400/500/600.
- Hindi: **Noto Sans Devanagari** (or Mukta), same sizes, line-height +10%.
- Scale (sp): 28 title · 22 heading · 18 subheading · 16 body · 14 secondary · 12 caption.
- Body line-height 1.5. Minimum text 12sp.

### 6.3 Shape and spacing
- Spacing scale: 4, 8, 12, 16, 20, 24, 32, 40.
- Radius: 12 inputs, 14 buttons, 16 cards, 999 chips/pills.
- Touch targets ≥ 48dp. Screen padding 16–24dp.
- Icons: outline, 1.75–2px stroke (Lucide or Material Symbols Outlined).

### 6.4 Key components
- **User bubble:** accent background, dark text, radius 16/16/4/16.
- **Bot answer card:** surface, border, 16 radius. Title in accent-text,
  summary 16sp, timing row with clock icon, three toggle pills (Why?,
  Sources, Remedies; filled accent when open), confidence caption.
- **Kundli-ready card:** 2×2 grid: Lagna, Moon sign, Nakshatra, Current dasha.
- **Topic chips:** surface, border, pill, 36dp high, wrap to two lines.
- **Input bar:** text field + camera (palm) + mic (v2) + send (accent square).
- **Empty, loading, error states** for every screen; loading = skeleton
  cards, never a spinner alone.

Reference prototype (approved look):
https://claude.ai/artifact/JNSuqYZQ8BiBJEEAujZ7Bo

---

## 7. Build phases

Build ONE phase at a time. At the end of each phase: list files created,
exact commands to run, test results, what the founder must check. Then STOP
and wait for "OK, next phase".

| Phase | Build | Done when |
|---|---|---|
| 0 | Repo setup, Docker Compose (Postgres, Redis), CI with pytest + lint, README | `docker compose up` and tests run green |
| 1 | Kundli engine (5.1) + `/chart` endpoint | Accuracy gate passes on 10 reference charts |
| 2 | Rules engine (5.2) + 200 seed rules | Evaluator unit tests pass; sample report for 3 charts |
| 3 | Chat pipeline (5.3), safety, templates in 3 languages | 50-question test set: ≥ 90% correct topic; 0 safety failures |
| 4 | API, auth (phone OTP), profiles, history, feedback, DPDP | Postman collection passes; delete-my-data works |
| 5 | Android app: onboarding, chat, answer cards, Kundli view, profiles, 3 languages | Runs on emulator and a real phone; matches the design system |
| 6 | Kundli Milan | 10 known matches give the same guna score as Drik Panchang |
| 7 | Palm pipeline (5.4) + in-chat camera | 20 test palms: lines detected or correctable in < 15 s |
| 8 | Payments (Razorpay test mode), free-question limit | Test purchase unlocks credits |
| 9 | Astrologer admin panel | Astrologer can approve/edit rules; only approved rules go live |
| 10 | Hardening + launch | Load test 50 req/s, crash-free ≥ 99.5%, Play Store listing, privacy policy, disclaimer |

---

## 8. Working rules for you

- Tests first for the engine, rules, matching and safety.
- When something is unclear, pick the simplest sensible option and record it
  in `DECISIONS.md` (date, decision, reason).
- Never commit secrets. `.env.example` lists every variable.
- Keep `README.md` current: setup, run, test, deploy.
- Small, readable functions with type hints and docstrings.
- Ask the founder only for things you cannot decide: reference charts,
  brand name, Razorpay keys, Play Store account.

Start with Phase 0.
