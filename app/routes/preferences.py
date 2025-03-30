from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.db import get_db
from app.models import UserPreference

router = APIRouter()


class PreferencesPayload(BaseModel):
    email_enabled: bool
    sms_enabled: bool
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


@router.get("/{user_id}", response_model=PreferencesPayload)
async def get_preferences(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    preference = result.scalar_one_or_none()
    if not preference:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return PreferencesPayload(
        email_enabled=preference.email_enabled,
        sms_enabled=preference.sms_enabled,
        email=preference.email if preference.email else None,  # Handle optional email
        phone_number=(
            preference.phone_number if preference.phone_number else None
        ),  # Handle optional phone number
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
        # Note: existing values for email and phone_number will be retained if not provided in payload
        # This allows for partial updates where only some fields are updated
        existing.email = payload.email if payload.email else existing.email
        existing.phone_number = (
            payload.phone_number if payload.phone_number else existing.phone_number
        )
    else:
        # Create new
        preference = UserPreference(
            user_id=user_id,
            email_enabled=payload.email_enabled,
            sms_enabled=payload.sms_enabled,
            # Note: email and phone_number can be None if not provided in the payload
            # This allows for flexibility in creating a new user preference without requiring all fields
            email=payload.email if payload.email else None,  # Handle optional email
            phone_number=(
                payload.phone_number if payload.phone_number else None
            ),  # Handle optional phone number
        )
        db.add(preference)

    await db.commit()
    return payload
