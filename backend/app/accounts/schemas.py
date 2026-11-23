"""Pydantic request/response models for auth, profiles, history, feedback."""

from datetime import date, datetime, time

from pydantic import BaseModel, Field


class OtpRequestRequest(BaseModel):
    phone_number: str = Field(min_length=6, max_length=20)


class OtpVerifyRequest(BaseModel):
    phone_number: str = Field(min_length=6, max_length=20)
    code: str = Field(min_length=4, max_length=10)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    relation: str = Field(default="self", pattern="^(self|family)$")
    language: str = Field(default="en", pattern="^(en|hi|hinglish)$")
    birth_date: date
    birth_time: time | None = None
    birth_time_unknown: bool = False
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180, description="East positive")
    timezone: str


class ProfileUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    language: str | None = Field(default=None, pattern="^(en|hi|hinglish)$")


class ProfileResponse(BaseModel):
    id: int
    name: str
    relation: str
    language: str
    birth_date: date
    birth_time: time | None
    birth_time_unknown: bool
    latitude: float
    longitude: float
    timezone: str
    created_at: datetime


class ChatHistoryItem(BaseModel):
    id: int
    message_text: str
    topic: str | None
    summary: str
    language: str
    confidence: str
    created_at: datetime
    is_accurate: bool | None


class FeedbackRequest(BaseModel):
    is_accurate: bool
