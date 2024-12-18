"""Conversations service module"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.chat.conversations import Conversations

logger = logging.getLogger(__name__)


class ConversationsService:
    """
    Сервис управления сущностью Conversations
    """

    def __init__(self, db_session: AsyncSession):
        """
        Инициализация сервиса ConversationsService.

        :param db_session: Асинхронная сессия базы данных.
        """
        self.db_session = db_session

    async def get_conversation_by_id(self, conversation_id: UUID) -> Conversations:
        """
        Получает объект Conversation модели по его идентификатору.

        :param conversation_id: Идентификатор объекта.
        :return: Экземпляр объекта модели Conversation.
        :raises HTTPException: Если объект не найден или произошла ошибка базы данных.
        """
        try:
            result = await self.db_session.execute(
                select(Conversations).where(Conversations.id == conversation_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=404, detail="Conversation not found")
            return obj
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in get_object_by_id: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")

    async def create_conversation(self, data: Dict[str, Any]) -> Conversations:
        """
        Создает новый объект Conversations модели в базе данных.

        :param data: Данные для создания объекта Conversations.
        :return: Созданный экземпляр объекта модели Conversations.
        :raises HTTPException: Если объект с уникальными полями уже существует или произошла ошибка базы данных.
        """
        user_first_id = data.get("user_first_id")
        user_second_id = data.get("user_second_id")

        if not user_first_id or not user_second_id:
            logger.error("Missing user IDs in the data")
            raise HTTPException(status_code=400, detail="Missing user IDs")

        if user_first_id == user_second_id:
            logger.error("Duplicate user_id (first user_id equals to the second one)")
            raise HTTPException(
                status_code=400, detail="Cannot create conversation with the same user"
            )

        # Поддержка консистентности. Подробности в документации (если ее еще нет, то будет)
        if user_first_id < user_second_id:
            user_first_id, user_second_id = user_first_id, user_second_id
        else:
            user_first_id, user_second_id = user_second_id, user_first_id

        try:
            # Проверка консистентности. Подробности в документации (если ее еще нет, то будет)
            result = await self.db_session.execute(
                select(Conversations).where(
                    Conversations.user_first_id == user_first_id,
                    Conversations.user_second_id == user_second_id,
                )
            )

            existing_conversation = result.scalar_one_or_none()

            if existing_conversation:
                logger.info(
                    f"Conversation between {user_first_id} and {user_second_id} already exists"
                )
                return existing_conversation

            new_conversation = Conversations(
                user_first_id=user_first_id, user_second_id=user_second_id
            )

            self.db_session.add(new_conversation)
            await self.db_session.commit()
            await self.db_session.refresh(new_conversation)
            return new_conversation

        except IntegrityError as ie:
            await self.db_session.rollback()
            logger.error(f"IntegrityError in create_conversation: {ie}")
            raise HTTPException(status_code=400, detail="Conversation already exists")

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in create_conversation: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")

    async def delete_conversation(self, conversation_id: UUID) -> Conversations:
        """
        Мягко удаляет Conversation, устанавливая флаг is_deleted и метку времени удаления.

        :param conversation_id: UUID идентификатор Conversation для удаления.
        :return: Обновлённый экземпляр Conversation с установленными флагами удаления.
        :raises HTTPException:
            - 404 Not Found если Conversation не существует.
            - 500 Internal Server Error для неожиданных ошибок сервера.
        """
        try:
            conversation = await self.get_conversation_by_id(conversation_id)

            conversation.is_deleted = True
            conversation.deleted_at = datetime.utcnow()

            self.db_session.add(conversation)
            await self.db_session.commit()
            await self.db_session.refresh(conversation)

            logger.info(f"Conversation {conversation_id} marked as deleted.")
            return conversation

        except HTTPException as he:
            raise he

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in delete_conversation: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")
