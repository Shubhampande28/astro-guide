"""Database models for Phase 4: accounts, profiles, chat history, feedback.

Birth date/time and latitude/longitude are encrypted at rest (DPDP,
principle 4). Name is kept in plain text -- it's needed for display and
profile switching (F8) and isn't itself astrologically identifying data.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

MAX_PROFILES_PER_USER = 5


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    consent_given_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profiles: Mapped[list["Profile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    relation: Mapped[str] = mapped_column(String(20), default="self")  # "self" | "family"
    language: Mapped[str] = mapped_column(String(10), default="en")

    birth_time_unknown: Mapped[bool] = mapped_column(Boolean, default=False)
    birth_date_enc: Mapped[str] = mapped_column(String(200))
    birth_time_enc: Mapped[str | None] = mapped_column(String(200))
    latitude_enc: Mapped[str] = mapped_column(String(200))
    longitude_enc: Mapped[str] = mapped_column(String(200))
    timezone: Mapped[str] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="profiles")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"))
    message_text_enc: Mapped[str] = mapped_column(String(2000))
    topic: Mapped[str | None] = mapped_column(String(30))
    summary_enc: Mapped[str] = mapped_column(String(4000))
    language: Mapped[str] = mapped_column(String(10))
    confidence: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profile: Mapped[Profile] = relationship(back_populates="chat_messages")
    feedback: Mapped["Feedback | None"] = relationship(
        back_populates="chat_message", cascade="all, delete-orphan", uselist=False
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_message_id: Mapped[int] = mapped_column(
        ForeignKey("chat_messages.id", ondelete="CASCADE"), unique=True
    )
    is_accurate: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chat_message: Mapped[ChatMessage] = relationship(back_populates="feedback")


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20), index=True)
    code_hash: Mapped[str] = mapped_column(String(200))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
