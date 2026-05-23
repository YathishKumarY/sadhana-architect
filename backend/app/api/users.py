from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import User, generate_uuid
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


@router.post("")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user profile."""
    db_user = User(
        id=generate_uuid(),
        name=user.name,
        default_tradition=user.default_tradition,
        default_experience_level=user.default_experience_level,
        default_duration_minutes=user.default_duration_minutes,
        excluded_practices=user.excluded_practices,
    )
    db.add(db_user)
    await db.commit()

    return {
        "id": db_user.id,
        "name": db_user.name,
        "default_tradition": db_user.default_tradition,
        "default_experience_level": db_user.default_experience_level,
        "default_duration_minutes": db_user.default_duration_minutes,
    }


@router.get("/me")
async def get_current_user(db: AsyncSession = Depends(get_db)):
    """Get the first (and typically only) user profile."""
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="No user profile found. Create one first.")

    return {
        "id": user.id,
        "name": user.name,
        "default_tradition": user.default_tradition,
        "default_experience_level": user.default_experience_level,
        "default_duration_minutes": user.default_duration_minutes,
        "excluded_practices": user.excluded_practices,
    }


@router.put("/me")
async def update_user(updates: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Update user profile."""
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="No user profile found")

    if updates.name is not None:
        user.name = updates.name
    if updates.default_tradition is not None:
        user.default_tradition = updates.default_tradition
    if updates.default_experience_level is not None:
        user.default_experience_level = updates.default_experience_level
    if updates.default_duration_minutes is not None:
        user.default_duration_minutes = updates.default_duration_minutes
    if updates.excluded_practices is not None:
        user.excluded_practices = updates.excluded_practices

    await db.commit()
    return {"status": "updated", "id": user.id}
