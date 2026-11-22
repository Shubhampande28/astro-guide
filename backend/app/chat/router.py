"""The /chat endpoint: runs a message through the full chat pipeline."""

from fastapi import APIRouter

from app.astro.chart import compute_chart
from app.chat.api_schemas import ChatRequest, ChatResponse
from app.chat.pipeline import handle_message
from app.rules.loader import load_all_rules

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def post_chat(request: ChatRequest) -> ChatResponse:
    chart = compute_chart(
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        tz_name=request.timezone,
        latitude_deg=request.latitude,
        longitude_east_deg=request.longitude,
    )
    card = handle_message(
        message=request.message,
        chart=chart,
        rules=list(load_all_rules()),
        language=request.language,
        previous_topic=request.previous_topic,
    )
    return ChatResponse.from_card(card)
