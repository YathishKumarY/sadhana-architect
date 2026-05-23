from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    default_tradition: str | None = None
    default_experience_level: str | None = None
    default_duration_minutes: int | None = None
    excluded_practices: list[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    name: str | None = None
    default_tradition: str | None = None
    default_experience_level: str | None = None
    default_duration_minutes: int | None = None
    excluded_practices: list[str] | None = None


class UserResponse(BaseModel):
    id: str
    name: str
    default_tradition: str | None
    default_experience_level: str | None
    default_duration_minutes: int | None
    excluded_practices: list[str] | None


class IngestRequest(BaseModel):
    title: str
    author: str | None = None
    tradition: str | None = None


class IngestStatusResponse(BaseModel):
    id: str
    title: str
    status: str
    total_chunks: int
    tradition: str | None
