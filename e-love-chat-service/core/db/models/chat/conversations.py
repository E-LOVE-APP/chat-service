from typing import List
from uuid import UUID

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from core.db.models.base import BaseModel


class Conversations(BaseModel):
    """
    Модель сущности разговора / диалога

    Атрибуты:
        user_first (UUID): ID первого участника диалога.
        user_second (UUID): ID второго участника диалога.
    """

    __tablename__ = "conversations"

    user_first_id: Column[UUID] = Column(String(36), unique=False, nullable=False)
    user_second_id: Column[UUID] = Column(String(36), unique=False, nullable=False)

    # Unique constraint that ensures that the conversation will be unique.
    __table_args__ = (
        UniqueConstraint("user_first_id", "user_second_id", name="unique_conversation"),
    )

    # 1 conversation HAS many messages
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
