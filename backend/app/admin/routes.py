from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas import UserOut
from app.auth.utils import get_current_admin_user
from app.database import get_db
from app.memos.models import VoiceMemo
from app.memos.schemas import VoiceMemoAdminOut

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)],
)


@router.get("/users", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[User]:
    """Return all registered users (admin only)."""
    result = await db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


@router.get("/memos", response_model=list[VoiceMemoAdminOut])
async def list_memos(db: AsyncSession = Depends(get_db)) -> list[VoiceMemo]:
    """Return all voice memos across every user (admin only)."""
    result = await db.execute(select(VoiceMemo).order_by(VoiceMemo.created_at.desc()))
    return list(result.scalars().all())
