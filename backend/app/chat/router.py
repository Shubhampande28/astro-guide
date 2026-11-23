"""The /chat endpoint: runs a message through the full chat pipeline,
scoped to one of the current user's profiles, and saves the exchange to
history (CLAUDE.md 5.3 steps 3 and 8, now that Phase 4 has profiles/DB)."""

from datetime import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.dependencies import get_current_user
from app.accounts.service import (
    decrypt_birth_date,
    decrypt_birth_time,
    decrypt_latitude,
    decrypt_longitude,
    get_owned_profile,
)
from app.astro.chart import compute_chart
from app.chat.api_schemas import ChatRequest, ChatResponse
from app.chat.pipeline import handle_message
from app.crypto import encrypt
from app.db import get_db
from app.models import ChatMessage, User
from app.rules.loader import load_all_rules

router = APIRouter(prefix="/chat", tags=["chat"])

# F6 (unknown birth time -> Moon-sign-only analysis with lower confidence)
# is not fully implemented yet; as a placeholder, a profile with no birth
# time computes its chart at local noon. See DECISIONS.md.
_UNKNOWN_BIRTH_TIME_DEFAULT = time(12, 0)


@router.post("", response_model=ChatResponse)
async def post_chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    profile = await get_owned_profile(request.profile_id, user, db)
    language = request.language or profile.language

    birth_time = decrypt_birth_time(profile)
    chart = compute_chart(
        birth_date=decrypt_birth_date(profile),
        birth_time=birth_time if birth_time else _UNKNOWN_BIRTH_TIME_DEFAULT,
        tz_name=profile.timezone,
        latitude_deg=decrypt_latitude(profile),
        longitude_east_deg=decrypt_longitude(profile),
    )
    card = handle_message(
        message=request.message,
        chart=chart,
        rules=list(load_all_rules()),
        language=language,
        previous_topic=request.previous_topic,
    )

    message = ChatMessage(
        profile_id=profile.id,
        message_text_enc=encrypt(request.message),
        topic=card.topic,
        summary_enc=encrypt(card.ai_rewritten_summary or card.summary),
        language=card.language,
        confidence=card.confidence,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    return ChatResponse.from_card(card, message_id=message.id)
