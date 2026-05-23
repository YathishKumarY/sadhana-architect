import os
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db.session import get_db
from app.db.models import IndexedText, generate_uuid
from app.db.vector_store import vector_store
from app.ingestion.pipeline import ingestion_pipeline

router = APIRouter()


@router.post("/upload")
async def upload_text(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(None),
    tradition: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF or EPUB file for ingestion."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".epub"):
        raise HTTPException(status_code=400, detail="Only PDF and EPUB files are supported")

    file_path = os.path.join(settings.texts_dir, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    text_record = IndexedText(
        id=generate_uuid(),
        title=title,
        author=author,
        tradition=tradition,
        file_path=file_path,
        file_type=ext.lstrip("."),
        status="pending",
    )
    db.add(text_record)
    await db.commit()

    return {"id": text_record.id, "title": title, "status": "pending"}


@router.post("/process/{text_id}")
async def process_text(text_id: str, db: AsyncSession = Depends(get_db)):
    """Trigger chunking and embedding for an uploaded text."""
    result = await db.execute(select(IndexedText).where(IndexedText.id == text_id))
    text_record = result.scalar_one_or_none()
    if not text_record:
        raise HTTPException(status_code=404, detail="Text not found")

    text_record.status = "processing"
    await db.commit()

    try:
        ingestion_result = await ingestion_pipeline.ingest(
            file_path=text_record.file_path,
            title=text_record.title,
            author=text_record.author,
            tradition=text_record.tradition,
        )

        text_record.status = "ready"
        text_record.total_chunks = ingestion_result["total_chunks"]
        from datetime import datetime
        text_record.ingested_at = datetime.utcnow()
        await db.commit()

        return {
            "id": text_id,
            "status": "ready",
            **ingestion_result,
        }
    except Exception as e:
        text_record.status = "error"
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{text_id}")
async def get_status(text_id: str, db: AsyncSession = Depends(get_db)):
    """Check ingestion status."""
    result = await db.execute(select(IndexedText).where(IndexedText.id == text_id))
    text_record = result.scalar_one_or_none()
    if not text_record:
        raise HTTPException(status_code=404, detail="Text not found")

    return {
        "id": text_record.id,
        "title": text_record.title,
        "status": text_record.status,
        "total_chunks": text_record.total_chunks,
    }


@router.get("/library")
async def list_library(db: AsyncSession = Depends(get_db)):
    """List all indexed texts."""
    result = await db.execute(select(IndexedText).order_by(IndexedText.title))
    texts = result.scalars().all()

    return {
        "texts": [
            {
                "id": t.id,
                "title": t.title,
                "author": t.author,
                "tradition": t.tradition,
                "status": t.status,
                "total_chunks": t.total_chunks,
                "ingested_at": t.ingested_at.isoformat() if t.ingested_at else None,
            }
            for t in texts
        ],
        "stats": vector_store.get_stats(),
    }
