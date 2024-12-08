from enum import Enum as PyEnum
from typing import List
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, relationship

from core.db.models.base import BaseModel


# TODO: extract to a different folder
class MessageStatus(PyEnum):
    SENT = "SENT"
    DELIVERED = "DELIVIRED"
    READ = "READ"


class Messages(BaseModel):
    """
    Модель сущности разговора / диалога

    Атрибуты:
        conversation_id (UUID): Внешний ключ на запись из таблицы conversation
        sender_id (UUID): ID пользователя, который отправил сообщение
        content (json? / TEXT): Содержимое сообщения
        timestamp -> created_at (BaseModel);
        status ENUM('sent', 'delivered', 'read'): статус сообщения

    """

    __tablename__ = "message"
    conversation_id: Column[UUID] = Column(ForeignKey("conversations.id"), nullable=False)
    sender_id: Column[UUID] = Column(String(36), nullable=False)
    content: Column[Text] = Column(Text, nullable=False)
    status: Mapped[MessageStatus] = Column(
        SQLEnum(MessageStatus, name="message_status"),
        default=MessageStatus.SENT,
        nullable=False,
    )

    # many messages HAS one conversation
    conversation: Mapped["Conversation"] = relationship("Conversations", back_populates="messages")
