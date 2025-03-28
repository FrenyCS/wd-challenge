from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.db import get_db
from app.models import UserPreference

router = APIRouter()


class PreferencesPayload(BaseModel):
    email_enabled: bool
    sms_enabled: bool


@router.get("/{user_id}", response_model=PreferencesPayload)
async def get_preferences(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    preference = result.scalar_one_or_none()
    if not preference:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return PreferencesPayload(
        email_enabled=preference.email_enabled, sms_enabled=preference.sms_enabled
    )


@router.post("/{user_id}", response_model=PreferencesPayload)
async def create_or_replace_preferences(
    user_id: str, payload: PreferencesPayload, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Overwrite
        existing.email_enabled = payload.email_enabled
        existing.sms_enabled = payload.sms_enabled
    else:
        # Create new
        preference = UserPreference(
            user_id=user_id,
            email_enabled=payload.email_enabled,
            sms_enabled=payload.sms_enabled,
        )
        db.add(preference)

    await db.commit()
    return payload
