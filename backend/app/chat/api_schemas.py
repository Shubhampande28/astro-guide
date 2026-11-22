"""Pydantic request/response models for the /chat endpoint."""

from datetime import date, time

from pydantic import BaseModel, Field

from app.chat.schemas import AnswerCard


class ChatRequest(BaseModel):
    message: str
    language: str = Field(default="en", pattern="^(en|hi|hinglish)$")
    previous_topic: str | None = None

    birth_date: date
    birth_time: time
    timezone: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180, description="East positive")


class ChatResponse(BaseModel):
    topic: str | None
    summary: str
    why: list[str]
    sources: list[str]
    timing: list[str]
    remedies: list[str]
    confidence: str
    language: str
    is_safety_response: bool
    is_declined: bool
    is_clarifying_question: bool
    ai_rewritten_summary: str | None

    @classmethod
    def from_card(cls, card: AnswerCard) -> "ChatResponse":
        return cls(**card.__dict__)
