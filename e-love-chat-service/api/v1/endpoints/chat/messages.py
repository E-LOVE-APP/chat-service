# chat_microservice/api/v1/endpoints/messages_endpoints.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from configuration.database import get_db_session
from core.db.models.chat.message import Message
from core.db.schemas.errors.httperror import HTTPError
from core.services.message.message_service import MessagesService

router = APIRouter(prefix="/messages", tags=["Messages"])


# TODO: change response-model to pydantic schemas
@router.get(
    "/{conversation_id}",
    # response_model=List[Message],
    responses={
        404: {"model": HTTPError},
        500: {"model": HTTPError},
    },
)
async def get_conversation_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get the list of messages for a specific Conversation.

    - **conversation_id**: The UUID of the Conversation.
    Returns all messages (in ascending order) for this conversation.
    """
    service = MessagesService(db)
    return await service.get_last_conversation_history(conversation_id)


@router.post(
    "/",
    # response_model=Message,
    responses={
        400: {"model": HTTPError},
        404: {"model": HTTPError},
        403: {"model": HTTPError},
        500: {"model": HTTPError},
    },
)
async def create_message(
    conversation_id: str,
    sender_id: str,
    recipient_id: str,
    content: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Create a new message in the given conversation.

    - **conversation_id**: UUID as a string
    - **sender_id**: UUID string for the sender
    - **recipient_id**: UUID string for the recipient
    - **content**: The text body of the message
    """
    payload = {
        "conversation_id": conversation_id,
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "content": content,
    }
    service = MessagesService(db)
    return await service.create_message(payload)


@router.put(
    "/{message_id}",
    # response_model=Message,
    responses={
        400: {"model": HTTPError},
        404: {"model": HTTPError},
        500: {"model": HTTPError},
    },
)
async def update_message(
    message_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Update the status of an existing message.

    - **message_id**: UUID of the message
    - **status**: New status (e.g. "READ", "DELIVERED", "SENT")
    """
    service = MessagesService(db)
    data = {"status": status}
    return await service.update_message(message_id, data)


@router.delete(
    "/{message_id}",
    responses={
        200: {"description": "Message deleted"},
        404: {"model": HTTPError},
        500: {"model": HTTPError},
    },
)
async def delete_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Delete a message record from the database.

    - **message_id**: UUID of the message to delete
    """
    service = MessagesService(db)
    await service.delete_message(message_id)
    return {"message": "Message deleted successfully."}
