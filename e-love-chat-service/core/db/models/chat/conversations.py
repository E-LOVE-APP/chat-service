from typing import List
from uuid import UUID

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint, Boolean, DateTime
from sqlalchemy.orm import Mapped, relationship

from core.db.models.base import BaseModel


class Conversations(BaseModel):
    """
    Модель сущности разговора / диалога;
    На данный момент, сущность разговора будет в себе хранить только 2ух пользователей. Поддержки групповых чатов нет, и, скорее всего, не будет.

    Атрибуты:
        user_first (UUID): ID первого участника диалога.
        user_second (UUID): ID второго участника диалога.
        is_deleted (Boolean): Флаг мягкого удаления разговора.
        deleted_at (DateTime): Время удаления разговора.
    """

    __tablename__ = "conversations"

    user_first_id: Column[UUID] = Column(String(36), unique=False, nullable=False)
    user_second_id: Column[UUID] = Column(String(36), unique=False, nullable=False)
    is_deleted: Column[bool] = Column(Boolean, default=False, nullable=False)
    deleted_at: Column[DateTime] = Column(DateTime(timezone=True), nullable=True)

    # Unique constraint that ensures that the conversation will be unique.
    __table_args__ = (
        UniqueConstraint("user_first_id", "user_second_id", name="unique_conversation"),
    )

    # 1 conversation HAS many messages. Удаляет ВСЕ записи messages из conversations, если один из пользователей решит удалить в чат (прямо как в телеге!), это обеспечивается через каскадное удаление.
    # TODO: возможно, стоит добавить "soft-deletion" ?
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
