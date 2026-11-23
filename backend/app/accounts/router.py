"""Auth (phone OTP), profiles, chat history, feedback, and DPDP
delete-my-data endpoints (CLAUDE.md Phase 4)."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts import otp
from app.accounts.dependencies import get_current_user
from app.accounts.jwt import create_access_token
from app.accounts.schemas import (
    ChatHistoryItem,
    FeedbackRequest,
    OtpRequestRequest,
    OtpVerifyRequest,
    ProfileCreateRequest,
    ProfileResponse,
    ProfileUpdateRequest,
    TokenResponse,
)
from app.accounts.service import (
    decrypt_birth_date,
    decrypt_birth_time,
    decrypt_latitude,
    decrypt_longitude,
    get_owned_profile,
)
from app.crypto import decrypt, encrypt
from app.db import get_db
from app.models import MAX_PROFILES_PER_USER, ChatMessage, Feedback, OtpCode, Profile, User

auth_router = APIRouter(prefix="/auth", tags=["auth"])
profiles_router = APIRouter(prefix="/profiles", tags=["profiles"])
me_router = APIRouter(prefix="/me", tags=["me"])


@auth_router.post("/otp/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_otp(request: OtpRequestRequest, db: AsyncSession = Depends(get_db)) -> None:
    code = otp.generate_code()
    db.add(
        OtpCode(
            phone_number=request.phone_number,
            code_hash=otp.hash_code(code),
            expires_at=otp.expiry_time(),
        )
    )
    await db.commit()
    otp.send_otp(request.phone_number, code)


@auth_router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(
    request: OtpVerifyRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    result = await db.execute(
        select(OtpCode)
        .where(OtpCode.phone_number == request.phone_number)
        .order_by(OtpCode.created_at.desc())
        .limit(1)
    )
    otp_row = result.scalar_one_or_none()

    # SQLite (used in tests) doesn't actually store timezone info, so a
    # read-back DateTime(timezone=True) column can come back naive even
    # though it was written as UTC-aware; Postgres (production) doesn't
    # have this problem, but this makes the comparison safe either way.
    expires_at = otp_row.expires_at if otp_row else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    if otp_row is None or expires_at < datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No valid OTP found; request a new one")
    if otp_row.attempts >= otp.MAX_VERIFY_ATTEMPTS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Too many attempts; request a new OTP")

    if not otp.verify_code(request.code, otp_row.code_hash):
        otp_row.attempts += 1
        await db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Incorrect code")

    result = await db.execute(select(User).where(User.phone_number == request.phone_number))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(phone_number=request.phone_number)
        db.add(user)
        await db.flush()

    await db.execute(delete(OtpCode).where(OtpCode.phone_number == request.phone_number))
    await db.commit()

    return TokenResponse(access_token=create_access_token(user.id))


@me_router.post("/consent", status_code=status.HTTP_204_NO_CONTENT)
async def give_consent(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    user.consent_given_at = datetime.now(UTC)
    await db.commit()


@me_router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_data(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """DPDP "delete my data": removes the user and every profile, chat
    message, and feedback row that belongs to them."""
    profile_ids_result = await db.execute(select(Profile.id).where(Profile.user_id == user.id))
    profile_ids = [row[0] for row in profile_ids_result.all()]

    if profile_ids:
        message_ids_result = await db.execute(
            select(ChatMessage.id).where(ChatMessage.profile_id.in_(profile_ids))
        )
        message_ids = [row[0] for row in message_ids_result.all()]
        if message_ids:
            await db.execute(delete(Feedback).where(Feedback.chat_message_id.in_(message_ids)))
            await db.execute(delete(ChatMessage).where(ChatMessage.id.in_(message_ids)))
        await db.execute(delete(Profile).where(Profile.id.in_(profile_ids)))

    await db.execute(delete(User).where(User.id == user.id))
    await db.commit()


def _profile_to_response(profile: Profile) -> ProfileResponse:
    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        relation=profile.relation,
        language=profile.language,
        birth_date=decrypt_birth_date(profile),
        birth_time=decrypt_birth_time(profile),
        birth_time_unknown=profile.birth_time_unknown,
        latitude=decrypt_latitude(profile),
        longitude=decrypt_longitude(profile),
        timezone=profile.timezone,
        created_at=profile.created_at,
    )


@profiles_router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    request: ProfileCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    if user.consent_given_at is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Consent is required before adding a profile"
        )

    count_result = await db.execute(select(Profile).where(Profile.user_id == user.id))
    if len(count_result.scalars().all()) >= MAX_PROFILES_PER_USER:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"Maximum {MAX_PROFILES_PER_USER} profiles per account"
        )

    profile = Profile(
        user_id=user.id,
        name=request.name,
        relation=request.relation,
        language=request.language,
        birth_time_unknown=request.birth_time_unknown,
        birth_date_enc=encrypt(request.birth_date.isoformat()),
        birth_time_enc=encrypt(request.birth_time.isoformat()) if request.birth_time else None,
        latitude_enc=encrypt(str(request.latitude)),
        longitude_enc=encrypt(str(request.longitude)),
        timezone=request.timezone,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return _profile_to_response(profile)


@profiles_router.get("", response_model=list[ProfileResponse])
async def list_profiles(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ProfileResponse]:
    result = await db.execute(select(Profile).where(Profile.user_id == user.id))
    return [_profile_to_response(p) for p in result.scalars().all()]


@profiles_router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    profile = await get_owned_profile(profile_id, user, db)
    return _profile_to_response(profile)


@profiles_router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    request: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    profile = await get_owned_profile(profile_id, user, db)
    if request.name is not None:
        profile.name = request.name
    if request.language is not None:
        profile.language = request.language
    await db.commit()
    await db.refresh(profile)
    return _profile_to_response(profile)


@profiles_router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    profile = await get_owned_profile(profile_id, user, db)
    message_ids_result = await db.execute(
        select(ChatMessage.id).where(ChatMessage.profile_id == profile.id)
    )
    message_ids = [row[0] for row in message_ids_result.all()]
    if message_ids:
        await db.execute(delete(Feedback).where(Feedback.chat_message_id.in_(message_ids)))
        await db.execute(delete(ChatMessage).where(ChatMessage.id.in_(message_ids)))
    await db.delete(profile)
    await db.commit()


@profiles_router.get("/{profile_id}/history", response_model=list[ChatHistoryItem])
async def get_history(
    profile_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ChatHistoryItem]:
    await get_owned_profile(profile_id, user, db)
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.profile_id == profile_id)
        .order_by(ChatMessage.created_at.desc())
    )
    items = []
    for message in result.scalars().all():
        feedback_result = await db.execute(
            select(Feedback).where(Feedback.chat_message_id == message.id)
        )
        feedback_row = feedback_result.scalar_one_or_none()
        items.append(
            ChatHistoryItem(
                id=message.id,
                message_text=decrypt(message.message_text_enc),
                topic=message.topic,
                summary=decrypt(message.summary_enc),
                language=message.language,
                confidence=message.confidence,
                created_at=message.created_at,
                is_accurate=feedback_row.is_accurate if feedback_row else None,
            )
        )
    return items


@profiles_router.post(
    "/{profile_id}/history/{message_id}/feedback", status_code=status.HTTP_204_NO_CONTENT
)
async def submit_feedback(
    profile_id: int,
    message_id: int,
    request: FeedbackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await get_owned_profile(profile_id, user, db)
    message = await db.get(ChatMessage, message_id)
    if message is None or message.profile_id != profile_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")

    existing_result = await db.execute(
        select(Feedback).where(Feedback.chat_message_id == message_id)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        existing.is_accurate = request.is_accurate
    else:
        db.add(Feedback(chat_message_id=message_id, is_accurate=request.is_accurate))
    await db.commit()
