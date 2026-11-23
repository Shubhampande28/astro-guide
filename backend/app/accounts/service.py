"""Shared profile helpers used by both the accounts and chat routers."""

from datetime import date, time

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crypto import decrypt
from app.models import Profile, User


async def get_owned_profile(profile_id: int, user: User, db: AsyncSession) -> Profile:
    profile = await db.get(Profile, profile_id)
    if profile is None or profile.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found")
    return profile


def decrypt_birth_date(profile: Profile) -> date:
    return date.fromisoformat(decrypt(profile.birth_date_enc))


def decrypt_birth_time(profile: Profile) -> time | None:
    return time.fromisoformat(decrypt(profile.birth_time_enc)) if profile.birth_time_enc else None


def decrypt_latitude(profile: Profile) -> float:
    return float(decrypt(profile.latitude_enc))


def decrypt_longitude(profile: Profile) -> float:
    return float(decrypt(profile.longitude_enc))
