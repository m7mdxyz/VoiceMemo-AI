import asyncio
import logging
from functools import lru_cache

import whisper
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.memos.models import VoiceMemo

logger = logging.getLogger(__name__)

WHISPER_MODEL_NAME = "base"


@lru_cache(maxsize=1)
def _get_model() -> whisper.Whisper:
    """Load and cache the local Whisper model (loaded once per process)."""
    return whisper.load_model(WHISPER_MODEL_NAME, device="cuda")


def _run_transcription(file_path: str, language: str | None) -> str:
    """Blocking call that runs the local Whisper model on an audio file."""
    model = _get_model()
    result = model.transcribe(file_path, language=language)
    return result["text"].strip()


async def transcribe_audio_task(memo_id: int, language: str | None = None) -> None:
    """Background task that transcribes a voice memo using a local Whisper model.

    Opens its own database session since the request-scoped session is closed
    by the time background tasks run. The blocking Whisper call is offloaded
    to a worker thread so it doesn't block the event loop.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(VoiceMemo).where(VoiceMemo.id == memo_id))
        memo = result.scalar_one_or_none()
        if memo is None:
            logger.warning("Voice memo %s not found for transcription", memo_id)
            return

        try:
            text = await asyncio.to_thread(_run_transcription, memo.file_path, language)
            memo.transcription = text
            memo.status = "completed"
        except Exception:
            logger.exception("Transcription failed for voice memo %s", memo_id)
            memo.status = "failed"
        finally:
            await db.commit()
