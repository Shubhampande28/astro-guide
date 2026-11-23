"""Pydantic request/response models for the /chat endpoint."""

from pydantic import BaseModel, Field

from app.chat.schemas import AnswerCard


class ChatRequest(BaseModel):
    profile_id: int
    message: str
    previous_topic: str | None = None
    language: str | None = Field(default=None, pattern="^(en|hi|hinglish)$")


class ChatResponse(BaseModel):
    message_id: int
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
    def from_card(cls, card: AnswerCard, message_id: int) -> "ChatResponse":
        return cls(message_id=message_id, **card.__dict__)
