from datetime import UTC, date, datetime, time

import pytest

from app.astro.chart import compute_chart
from app.rules.context import ChartContext


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
