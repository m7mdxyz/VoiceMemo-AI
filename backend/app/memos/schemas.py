from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VoiceMemoOut(BaseModel):
    id: int
    filename: str
    status: str
    transcription: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VoiceMemoAdminOut(VoiceMemoOut):
    user_id: int
