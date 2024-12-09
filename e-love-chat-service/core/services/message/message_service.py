import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from core.db.models.chat.conversations import Conversations
from core.db.models.chat.message import Messages, MessageStatus

logger = logging.getLogger(__name__)


class MessagesService:
    """
    Service for managing Messages entities.

    This service provides methods to interact with the Messages model, including retrieving,
    creating, updating, and deleting message records in the database. It ensures data integrity
    and handles potential exceptions that may arise during database operations.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initializes the MessagesService with a given database session.

        :param db_session: An instance of AsyncSession for interacting with the database asynchronously.
        """
        self.db_session = db_session

    async def get_message_by_id(self, message_id: UUID) -> Messages:
        """
        Retrieves a Message object from the database by its unique identifier.

        :param message_id: The UUID of the Message to retrieve.
        :return: An instance of the Messages model corresponding to the provided ID.
        :raises HTTPException:
            - 404 Not Found if the Message does not exist.
            - 500 Internal Server Error for unexpected server errors.
        """
        try:

            result = await self.db_session.execute(
                select(Messages).where(Messages.id == message_id)
            )

            message = result.scalar_one_or_none()

            if not message:
                raise HTTPException(status_code=404, detail="Message not found")
            return message

        except HTTPException as he:
            raise he

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in get_message_by_id: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")

    async def create_message(self, data: Dict[str, Any]) -> Messages:
        """
        Creates a new Message record in the database within a specified conversation.

        This method ensures that:
        1. The conversation_id and sender_id are provided and valid.
        2. The specified conversation exists to associate the message with.
        3. The content of the message is provided.
        4. The message is created with an initial status of SENT.
        5. Handles potential IntegrityError exceptions that may arise from database constraints.
        6. Rolls back the session and logs errors for any unexpected exceptions.

        :param data: A dictionary containing the data for creating a new Message.
        :return: An instance of the newly created Messages model.
        :raises HTTPException:
            - 400 Bad Request if required fields are missing.
            - 404 Not Found if the specified conversation does not exist.
            - 500 Internal Server Error for unexpected server errors.
        """

        conversation_id = data.get("conversation_id")
        sender_id = data.get("sender_id")
        content = data.get("content")

        if not conversation_id or not sender_id or not content:
            logger.error("Missing required fields in the data")
            raise HTTPException(status_code=400, detail="Missing required fields")

        try:
            # Check if the specified conversation exists
            result = await self.db_session.execute(
                select(Conversations).where(Conversations.id == conversation_id)
            )

            conversation = result.scalar_one_or_none()

            if not conversation:
                logger.error(f"Conversation {conversation_id} does not exist")
                raise HTTPException(status_code=404, detail="Conversation not found")

            new_message = Messages(
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=content,
                status=MessageStatus.SENT,
            )

            self.db_session.add(new_message)
            await self.db_session.commit()
            await self.db_session.refresh(new_message)
            logger.info(f"Created new message with ID {new_message.id}")
            return new_message

        except HTTPException as he:
            raise he

        except IntegrityError as ie:
            await self.db_session.rollback()
            logger.error(f"IntegrityError in create_message: {ie}")
            raise HTTPException(status_code=400, detail="Invalid data provided")

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in create_message: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")

    async def update_message(self, message_id: UUID, data: Dict[str, Any]) -> Messages:
        """
        Updates the status of an existing Message in the database.

        This method performs the following steps:
        1. Retrieves the Message with the specified ID.
        2. Updates the Message's status based on the provided data.
        3. Commits the transaction to persist the changes.
        4. Refreshes the Message instance to reflect the updated status.
        5. Logs the update action.

        :param message_id: The UUID of the Message to update.
        :param data: A dictionary containing the fields to update (e.g., status).
        :return: The updated Messages instance.
        :raises HTTPException:
            - 400 Bad Request if the status provided is invalid.
            - 404 Not Found if the Message does not exist.
            - 500 Internal Server Error for unexpected server errors.
        """
        new_status = data.get("status")

        # Validate that the new status is provided
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

        except HTTPException as he:
            raise he

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in update_message: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")

    async def delete_message(self, message_id: UUID) -> None:
        """
        Deletes a Message record from the database.

        This method performs the following steps:
        1. Retrieves the Message with the specified ID.
        2. Deletes the Message from the session.
        3. Commits the transaction to remove the record from the database.
        4. Logs the deletion action.

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

        except HTTPException as he:
            raise he

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error in delete_message: {e}")
            raise HTTPException(status_code=500, detail="Unexpected server error!")
