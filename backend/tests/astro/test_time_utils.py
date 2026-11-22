from datetime import date, time

from app.astro.time_utils import to_utc


def test_modern_ist_offset_is_5_30() -> None:
    utc = to_utc(date(2024, 6, 15), time(12, 0), "Asia/Kolkata")
    assert utc.hour == 6
    assert utc.minute == 30


def test_pre_1941_offset_is_5_30() -> None:
    utc = to_utc(date(1930, 1, 1), time(12, 0), "Asia/Kolkata")
    assert utc.hour == 6
    assert utc.minute == 30


def test_wartime_1943_offset_is_6_30() -> None:
    # CLAUDE.md 5.1 calls this out by name: India used +6:30 in 1942-45.
    utc = to_utc(date(1943, 3, 1), time(12, 0), "Asia/Kolkata")
    assert utc.hour == 5
    assert utc.minute == 30
