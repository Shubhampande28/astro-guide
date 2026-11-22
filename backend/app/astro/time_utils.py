"""Local civil time -> UTC, using the IANA timezone database so historical
offsets (e.g. India at +6:30 before 1 Sept 1947, +5:53:20 before 1941) are
handled correctly by `zoneinfo` rather than assumed to always be +5:30.
"""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo


def to_utc(birth_date: date, birth_time: time, tz_name: str) -> datetime:
    """Convert a local civil date+time in `tz_name` to an aware UTC datetime."""
    local_dt = datetime.combine(birth_date, birth_time, tzinfo=ZoneInfo(tz_name))
    return local_dt.astimezone(ZoneInfo("UTC"))
