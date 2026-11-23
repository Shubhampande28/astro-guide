import asyncio
import os
import tempfile
import uuid

# Must happen before any `app.*` import that could trigger get_settings():
# tests use a throwaway SQLite file instead of the real Postgres database.
_db_fd, _DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_DB_PATH}"

from datetime import UTC, date, datetime, time  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.accounts import otp  # noqa: E402
from app.astro.chart import compute_chart  # noqa: E402
from app.db import Base, get_engine  # noqa: E402
from app.main import app  # noqa: E402
from app.rules.context import ChartContext  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_test_database():
    async def _create() -> None:
        async with get_engine().begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create())
    yield
    # The engine must release its connections before the file can be
    # deleted on Windows.
    asyncio.run(get_engine().dispose())
    os.remove(_DB_PATH)


@pytest.fixture
def sample_chart():
    """1990-05-15 08:30 IST, New Delhi. Lagna Gemini; see test comments for
    the known graha placements this fixture produces."""
    return compute_chart(
        birth_date=date(1990, 5, 15),
        birth_time=time(8, 30),
        tz_name="Asia/Kolkata",
        latitude_deg=28.6139,
        longitude_east_deg=77.2090,
        as_of=datetime(1990, 5, 15, 3, 0, tzinfo=UTC),
    )


@pytest.fixture
def sample_ctx(sample_chart):
    return ChartContext(chart=sample_chart)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def login(client, monkeypatch):
    """Returns a function that registers/logs in a phone number via the
    real OTP flow and returns a bearer-auth header dict."""

    def _login(phone_number: str) -> dict[str, str]:
        captured = {}

        def fake_send_otp(phone: str, code: str) -> None:
            captured["code"] = code

        monkeypatch.setattr(otp, "send_otp", fake_send_otp)

        response = client.post("/auth/otp/request", json={"phone_number": phone_number})
        assert response.status_code == 204

        response = client.post(
            "/auth/otp/verify", json={"phone_number": phone_number, "code": captured["code"]}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _login


@pytest.fixture
def auth_headers(login):
    # A fresh phone number per test: the test database persists for the
    # whole session, so reusing one number would let unrelated tests pile
    # up profiles on the same account (e.g. breaking the max-5 limit test).
    unique_number = f"+91{uuid.uuid4().int % 10**10:010d}"
    return login(unique_number)


@pytest.fixture
def consented_headers(client, auth_headers):
    response = client.post("/me/consent", headers=auth_headers)
    assert response.status_code == 204
    return auth_headers


@pytest.fixture
def profile_payload():
    return {
        "name": "Test User",
        "relation": "self",
        "language": "en",
        "birth_date": "1990-05-15",
        "birth_time": "08:30:00",
        "birth_time_unknown": False,
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata",
    }


@pytest.fixture
def created_profile(client, consented_headers, profile_payload):
    response = client.post("/profiles", json=profile_payload, headers=consented_headers)
    assert response.status_code == 201
    return response.json()
