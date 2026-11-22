# Third-party licences

Every dependency's licence is checked before it is added, per CLAUDE.md
principle 2 (free and accurate, no AGPL/GPL). This list is updated whenever a
new dependency is added.

| Package | Licence | Notes |
|---|---|---|
| Skyfield | MIT | Core astro engine, used with NASA JPL DE440s ephemeris (public domain, NASA/JPL) |
| FastAPI | MIT | Web framework |
| Pydantic | MIT | Data validation |
| SQLAlchemy | MIT | ORM |
| asyncpg | Apache 2.0 | Postgres driver |
| Alembic | MIT | DB migrations |
| redis-py | MIT | Redis client |
| python-jose | MIT | JWT handling |
| PyYAML | MIT | Rules file parsing |
| tzdata | Apache 2.0 / MIT | IANA timezone database (needed on Windows and some minimal Linux images, which don't ship it by default) |
| pytest | MIT | Testing |
| ruff | MIT | Linting |
| black | MIT | Formatting |

**Never add:** pyswisseph (AGPL), libephemeris, or any other AGPL/GPL-licensed
library, per CLAUDE.md principle 2.
