import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.rag import rag_pipeline
from app.db.session import get_db
from app.db.models import Practice, generate_uuid
from app.schemas.practice import PracticeRequest, PracticeResponse, GeneratedPractice

router = APIRouter()


@router.post("/generate")
async def generate_practice(request: PracticeRequest, db: AsyncSession = Depends(get_db)):
    """Generate a personalized practice based on current state."""
    practice = await rag_pipeline.generate(request)

    db_practice = Practice(
        id=generate_uuid(),
        input_physical_state=request.physical_state,
        input_mental_state=request.mental_state,
        input_emotional_state=request.emotional_state,
        input_time_minutes=request.time_available_minutes,
        input_tradition=request.tradition_preference,
        input_experience_level=request.experience_level,
        generated_practice=practice.model_dump(),
    )
    db.add(db_practice)
    await db.commit()

    return {
        "id": db_practice.id,
        "created_at": db_practice.created_at.isoformat(),
        "practice": practice.model_dump(),
    }


@router.post("/generate/stream")
async def generate_practice_stream(request: PracticeRequest):
    """Stream practice generation via Server-Sent Events."""

    async def event_stream():
        async for token in rag_pipeline.generate_stream(request):
            yield f"data: {json.dumps({'token': token})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/{practice_id}")
async def get_practice(practice_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a saved practice by ID."""
    result = await db.execute(select(Practice).where(Practice.id == practice_id))
    practice = result.scalar_one_or_none()
    if not practice:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Practice not found")

    return {
        "id": practice.id,
        "created_at": practice.created_at.isoformat(),
        "practice": practice.generated_practice,
        "rating": practice.rating,
        "notes": practice.notes,
        "request": {
            "physical_state": practice.input_physical_state,
            "mental_state": practice.input_mental_state,
            "emotional_state": practice.input_emotional_state,
            "time_available_minutes": practice.input_time_minutes,
            "experience_level": practice.input_experience_level,
            "tradition_preference": practice.input_tradition,
        },
    }


@router.patch("/{practice_id}/rate")
async def rate_practice(
    practice_id: str,
    rating: int,
    notes: str | None = None,
    would_repeat: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Rate a completed practice."""
    result = await db.execute(select(Practice).where(Practice.id == practice_id))
    practice = result.scalar_one_or_none()
    if not practice:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Practice not found")

    practice.rating = rating
    practice.notes = notes
    practice.would_repeat = would_repeat
    await db.commit()

    return {"status": "rated", "id": practice_id, "rating": rating}
