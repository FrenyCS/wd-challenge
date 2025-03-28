# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.db import Base

class NotificationStatus(PyEnum):
    pending = "pending"
    sent = "sent"
    failed = "failed"

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)

    notifications = relationship("Notification", back_populates="user")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_preferences.user_id"))
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    send_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.pending)
    channel = Column(String)  # 'email' or 'sms'

    user = relationship("UserPreference", back_populates="notifications")