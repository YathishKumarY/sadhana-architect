import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    default_tradition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    default_experience_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    default_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    excluded_practices: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Practice(Base):
    __tablename__ = "practices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    input_physical_state: Mapped[str] = mapped_column(Text)
    input_mental_state: Mapped[str] = mapped_column(Text)
    input_emotional_state: Mapped[str] = mapped_column(Text)
    input_time_minutes: Mapped[int] = mapped_column(Integer)
    input_tradition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    input_experience_level: Mapped[str] = mapped_column(String(20))
    generated_practice: Mapped[dict] = mapped_column(JSON)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    would_repeat: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


class IndexedText(Base):
    __tablename__ = "indexed_texts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500))
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tradition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000))
    file_type: Mapped[str] = mapped_column(String(10))
    total_chunks: Mapped[int] = mapped_column(Integer, default=0)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
