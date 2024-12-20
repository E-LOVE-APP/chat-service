"""
WebSocket Integration for E-Love Chat Service

This module integrates the MessagesService and ConversationsService with FastAPI's WebSocket
functionality to enable real-time chat capabilities. It allows clients to connect via WebSockets,
join conversations, send messages, and receive messages from other participants in real time.

Usage:
This module is intended to be included in the main FastAPI application. It provides WebSocket endpoints 
for user conversations that clients can connect to for real-time chat interactions. Ensure that the application is properly
configured with the necessary services and database connections before integrating this module.
"""

import asyncio
import logging
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from configuration.database import get_db_session
from core.db.models.chat.conversations import Conversations
from core.db.models.chat.message import Message
from core.db.schemas.chat.conversation import CreateConversationOutput, CreateConversationRequest
from core.services.conversations.conversations_service import ConversationsService
from core.services.message.message_service import MessagesService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

# TODO: add docstrings to the funcs


@router.post("/conversations", response_model=CreateConversationOutput)
async def create_chat_conversation(
    request_data: CreateConversationRequest, db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new conversation between two users.

    This endpoint takes a JSON body containing user_first_id and user_second_id (both as strings),
    creates a conversation in the database, and returns the created conversation details.
    """
    service = ConversationsService(db)
    conversation = await service.create_conversation(
        {"user_first_id": request_data.user_first_id, "user_second_id": request_data.user_second_id}
    )

    return CreateConversationOutput(
        id=conversation.id,
        user_first_id=conversation.user_first_id,
        user_second_id=conversation.user_second_id,
    )


# TODO: maybe I can also get rid of str-casting here using pydantic?
@router.websocket("/{conversation_id}")
async def chat_endpoint(
    websocket: WebSocket, conversation_id: UUID, db: AsyncSession = Depends(get_db_session)
):
    conversations_service = ConversationsService(db)
    messages_service = MessagesService(db)

    try:
        await conversations_service.get_conversation_by_id(str(conversation_id))
    except HTTPException as e:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    while True:
        try:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "send_message":
                payload = data["data"]
                sender_id = payload["sender_id"]
                recipient_id = payload["recipient_id"]
                content = payload["content"]

                new_message = await messages_service.create_message(
                    {
                        "conversation_id": str(conversation_id),
                        "sender_id": str(sender_id),
                        "recipient_id": str(recipient_id),
                        "content": content,
                    }
                )

                await websocket.send_json(
                    {
                        "action": "message_saved",
                        "data": {
                            "sender_id": sender_id,
                            "recipient_id": recipient_id,
                            "content": content,
                        },
                    }
                )

        except HTTPException as he:
            await db.rollback()
            await websocket.send_json({"error": he.detail})
            continue

        except WebSocketDisconnect:
            break

        except Exception as e:
            await db.rollback()
            await websocket.send_json({"error": "Unexpected server error."})
            break
