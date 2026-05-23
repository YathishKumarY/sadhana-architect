from pydantic import BaseModel, Field


class PracticeRequest(BaseModel):
    physical_state: str = Field(..., description="Current physical state and sensations")
    mental_state: str = Field(..., description="Current mental state")
    emotional_state: str = Field(..., description="Current emotional state")
    time_available_minutes: int = Field(30, ge=10, le=120)
    experience_level: str = Field("intermediate", pattern="^(beginner|intermediate|advanced)$")
    tradition_preference: str | None = Field(None, description="hatha, raja, tantra, vedanta, or None for all")
    focus_areas: list[str] = Field(default_factory=lambda: ["pranayama", "asana", "meditation"])
    exclude: list[str] = Field(default_factory=list, description="Practices to exclude")


class Citation(BaseModel):
    id: str
    book: str
    chapter: str | int | None = None
    verse: str | int | None = None
    quote: str
    relevance: str


class PranayamaStep(BaseModel):
    name: str
    sanskrit_name: str | None = None
    duration_minutes: int
    instructions: str
    contraindications: str | None = None
    source_citation_id: str | None = None


class AsanaStep(BaseModel):
    name: str
    sanskrit_name: str | None = None
    duration_minutes: int
    instructions: str
    contraindications: str | None = None
    source_citation_id: str | None = None


class MeditationStep(BaseModel):
    name: str
    technique: str
    duration_minutes: int
    instructions: str
    source_citation_id: str | None = None


class GeneratedPractice(BaseModel):
    title: str
    duration_minutes: int
    intention: str
    pranayama: list[PranayamaStep] = Field(default_factory=list)
    asana: list[AsanaStep] = Field(default_factory=list)
    meditation: MeditationStep | None = None
    closing_reflection: str | None = None
    citations: list[Citation] = Field(default_factory=list)


class PracticeResponse(BaseModel):
    id: str
    created_at: str
    request: PracticeRequest
    practice: GeneratedPractice
    rating: int | None = None
    notes: str | None = None
