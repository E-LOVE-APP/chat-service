# chat_microservice/api/v1/endpoints/conversations_endpoints.py

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from configuration.database import get_db_session
from core.db.models.chat.conversations import Conversations
from core.db.schemas.errors.httperror import HTTPError
from core.services.conversations.conversations_service import ConversationsService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


# TODO: change response-models to pydantic?
@router.get(
    "/{conversation_id}",
    # response_model=Conversations,
    responses={
        404: {"model": HTTPError, "description": "Conversation not found"},
        500: {"model": HTTPError},
    },
)
async def get_conversation_by_id(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve a single Conversation by its UUID.

    - **conversation_id**: The UUID of the Conversation.
    Returns the Conversation object if it exists, otherwise 404.
    """
    service = ConversationsService(db)
    return await service.get_conversation_by_id(conversation_id)


@router.delete(
    "/{conversation_id}",
    responses={
        200: {"description": "Conversation marked as deleted."},
        404: {"model": HTTPError},
        500: {"model": HTTPError},
    },
)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Soft-delete an existing conversation by setting is_deleted to True.

    - **conversation_id**: UUID of the conversation to delete.
    Returns 404 if not found.
    """
    service = ConversationsService(db)
    deleted_conversation = await service.delete_conversation(conversation_id)
    return {"message": f"Conversation {deleted_conversation.id} is deleted.", "deleted": True}
