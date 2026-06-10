from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.utils import get_current_user
from app.database import get_db
from app.memos.models import VoiceMemo
from app.memos.schemas import VoiceMemoOut
from app.memos.services import save_upload_file
from app.memos.tasks import transcribe_audio_task

router = APIRouter(prefix="/memos", tags=["memos"])


@router.post("/upload", response_model=VoiceMemoOut, status_code=status.HTTP_202_ACCEPTED)
async def upload_memo(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VoiceMemo:
    """Upload an audio file and schedule it for background transcription.

    `language` is an optional ISO-639-1 code (e.g. "en", "ar"). If omitted or
    empty, Whisper will auto-detect the spoken language.
    """
    stored_filename, file_path = await save_upload_file(file, current_user.id)

    memo = VoiceMemo(
        filename=stored_filename,
        file_path=file_path,
        status="processing",
        user_id=current_user.id,
    )
    db.add(memo)
    await db.commit()
    await db.refresh(memo)

    background_tasks.add_task(transcribe_audio_task, memo.id, language or None)

    return memo


@router.get("/history", response_model=list[VoiceMemoOut])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[VoiceMemo]:
    """Return all voice memos belonging to the current user, newest first."""
    result = await db.execute(
        select(VoiceMemo)
        .where(VoiceMemo.user_id == current_user.id)
        .order_by(VoiceMemo.created_at.desc())
    )
    return list(result.scalars().all())
