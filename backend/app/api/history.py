from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.db.models import Practice

router = APIRouter()


@router.get("")
async def get_practice_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tradition: str | None = None,
    min_rating: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List past practices with optional filters."""
    query = select(Practice).order_by(desc(Practice.created_at))

    if tradition:
        query = query.where(Practice.input_tradition == tradition)
    if min_rating:
        query = query.where(Practice.rating >= min_rating)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    practices = result.scalars().all()

    return {
        "practices": [
            {
                "id": p.id,
                "created_at": p.created_at.isoformat(),
                "title": p.generated_practice.get("title", "Untitled Practice") if p.generated_practice else "Untitled",
                "duration_minutes": p.input_time_minutes,
                "tradition": p.input_tradition,
                "experience_level": p.input_experience_level,
                "rating": p.rating,
                "physical_state": p.input_physical_state,
                "mental_state": p.input_mental_state,
                "emotional_state": p.input_emotional_state,
            }
            for p in practices
        ],
        "total": len(practices),
        "offset": offset,
        "limit": limit,
    }
