import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.config import settings


async def save_upload_file(file: UploadFile, user_id: int) -> tuple[str, str]:
    """Asynchronously save an uploaded audio file to the storage directory.

    Returns a tuple of (stored_filename, file_path).
    """
    storage_dir = Path(settings.storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "").suffix
    stored_filename = f"{user_id}_{uuid.uuid4().hex}{extension}"
    file_path = storage_dir / stored_filename

    async with aiofiles.open(file_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            await out_file.write(chunk)

    return stored_filename, str(file_path)
