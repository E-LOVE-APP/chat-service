import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from core.db.models.chat.conversations import Conversations
from core.db.models.chat.message import Message, MessageStatus

logger = logging.getLogger(__name__)


class MessagesService:
    """
    Service for managing Messages entities.
    Provides CRUD operations on Messages with proper error handling and validations.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initializes the MessagesService with a given database session.

        :param db_session: An instance of AsyncSession for interacting with the database asynchronously.
        """
        self.db_session = db_session

    async def get_message_by_id(self, message_id: UUID) -> Message:
        """
        Retrieves a Message object from the database by its unique identifier.

        :param message_id: The UUID of the Message to retrieve.
        :return: An instance of the Message model corresponding to the provided ID.
        :raises HTTPException:
            - 404 Not Found if the Message does not exist.
            - 500 Internal Server Error for unexpected server errors.
        """
        try:
            result = await self.db_session.execute(select(Message).where(Message.id == message_id))
            message = result.scalar_one_or_none()
            if not message:
                raise HTTPException(status_code=404, detail="Message not found")
            return message
        except HTTPException:
            raise
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in get_message_by_id: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")

    async def create_message(self, data: Dict[str, Any]) -> Message:
        """
        Creates a new Message record in the database within a specified conversation.

        Validations:
        - conversation_id, sender_id, content must be present.
        - conversation must exist.
        - sender_id and recipient_id (if provided) must belong to this conversation.
        - message is created with SENT status.

        :param data: A dictionary containing the data for creating a new Message.
        :return: An instance of the newly created Message model.
        :raises HTTPException:
            - 400 Bad Request if required fields are missing.
            - 404 Not Found if the specified conversation does not exist.
            - 403 Forbidden if sender or recipient are not participants of the conversation.
            - 500 Internal Server Error for unexpected server errors.
        """

        # Extract fields
        conversation_id = data.get("conversation_id")
        sender_id = data.get("sender_id")
        recipient_id = data.get("recipient_id")
        content = data.get("content")

        # Basic field checks
        if not conversation_id or not sender_id or not content:
            logger.error("Missing required fields in the data")
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Convert to UUID where appropriate
        try:
            conversation_uuid = str(conversation_id)
            print(conversation_uuid)
            sender_uuid = UUID(str(sender_id))
            recipient_uuid = UUID(str(recipient_id)) if recipient_id else None
        except ValueError:
            logger.error("Invalid UUID format for sender/recipient")
            raise HTTPException(status_code=400, detail="Invalid UUID format")

        try:
            result = await self.db_session.execute(
                select(Conversations).where(Conversations.id == conversation_uuid)
            )
            conversation = result.scalar_one_or_none()
            if not conversation:
                logger.error(f"Conversation {conversation_uuid} does not exist")
                raise HTTPException(status_code=404, detail="Conversation not found")

            user_first_uuid = UUID(str(conversation.user_first_id))
            user_second_uuid = UUID(str(conversation.user_second_id))
            allowed_users = {user_first_uuid, user_second_uuid}

            if sender_uuid not in allowed_users:
                logger.error(
                    f"Sender {sender_uuid} does not belong to conversation {conversation_uuid}"
                )
                raise HTTPException(
                    status_code=403, detail="Sender not authorized in this conversation"
                )

            if recipient_uuid and recipient_uuid not in allowed_users:
                logger.error(
                    f"Recipient {recipient_uuid} does not belong to conversation {conversation_uuid}"
                )
                raise HTTPException(
                    status_code=403, detail="Recipient not authorized in this conversation"
                )

            # Create message
            new_message = Message(
                conversation_id=conversation_uuid,
                sender_id=sender_uuid,
                content=content,
                status=MessageStatus.SENT,
            )

            self.db_session.add(new_message)
            await self.db_session.commit()
            await self.db_session.refresh(new_message)
            logger.info(f"Created new message with ID {new_message.id}")
            return new_message

        except HTTPException:
            raise
        except IntegrityError as ie:
            await self.db_session.rollback()
            logger.error(f"IntegrityError in create_message: {ie}")
            raise HTTPException(status_code=400, detail="Invalid data provided")
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in create_message: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")

    async def update_message(self, message_id: UUID, data: Dict[str, Any]) -> Message:
        """
        Updates the status of an existing Message in the database.

        :param message_id: The UUID of the Message to update.
        :param data: A dictionary containing the fields to update (e.g., status).
        :return: The updated Message instance.
        :raises HTTPException:
            - 400 Bad Request if the status provided is invalid.
            - 404 Not Found if the Message does not exist.
            - 500 Internal Server Error for unexpected server errors.
        """
        new_status = data.get("status")

        if not new_status:
            logger.error("Missing status field in the data")
            raise HTTPException(status_code=400, detail="Missing status field")

        try:
            new_status_enum = MessageStatus(new_status)
        except ValueError:
            logger.error(f"Invalid status value provided: {new_status}")
            raise HTTPException(status_code=400, detail="Invalid status value")

        try:
            message = await self.get_message_by_id(message_id)
            message.status = new_status_enum
            self.db_session.add(message)
            await self.db_session.commit()
            await self.db_session.refresh(message)
            logger.info(f"Updated message {message_id} to status {new_status_enum}")
            return message
        except HTTPException:
            raise
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in update_message: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")

    async def delete_message(self, message_id: UUID) -> None:
        """
        Deletes a Message record from the database.

        :param message_id: The UUID of the Message to delete.
        :return: None
        :raises HTTPException:
            - 404 Not Found if the Message does not exist.
            - 500 Internal Server Error for unexpected server errors.
        """
        try:
            message = await self.get_message_by_id(message_id)
            await self.db_session.delete(message)
            await self.db_session.commit()
            logger.info(f"Deleted message with ID {message_id}")
        except HTTPException:
            raise
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in delete_message: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")
