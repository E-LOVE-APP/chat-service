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
from core.db.schemas.chat.websocket_actions import SendMessageAction, SendMessageData
from core.services.conversations.conversations_service import ConversationsService
from core.services.message.message_service import MessagesService
from handlers.chat.send_message_handler import handle_send_message
from utils.chat.chat_responses import error_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(tags=["Conversations", "Conversations via WebSockets"])


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


@router.websocket("/{conversation_id}")
async def conversation_messages_websocket(
    websocket: WebSocket, conversation_id: UUID, db: AsyncSession = Depends(get_db_session)
):
    """
    WebSocket endpoint for real-time messaging within a conversation.

    Connect to ws://<host>/chat/{conversation_id} and send JSON messages:
    {
      "action": "send_message",
      "data": {
        "sender_id": "<uuid>",
        "recipient_id": "<uuid>",
        "content": "Hello!"
      }
    }

    If successful, responds with:
    {
      "action": "message_saved",
      "data": {
        "sender_id": "<uuid>",
        "recipient_id": "<uuid>",
        "content": "..."
      }
    }

    On error:
    {
      "error": "Error detail"
    }
    """
    conversations_service = ConversationsService(db)

    try:
        await conversations_service.get_conversation_by_id(str(conversation_id))
    except HTTPException as e:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    # If we anticipate more actions, we can define a dispatcher:
    action_handlers = {
        "send_message": handle_send_message,
        # TODO: In the future, add "update_message": handle_update_message, etc.
    }

    while True:
        try:
            raw_data = await websocket.receive_json()
            # Validate incoming message using pydantic schema
            message_action = SendMessageAction(**raw_data)

            handler = action_handlers.get(message_action.action)
            if handler:
                response = await handler(
                    db,
                    conversation_id=str(conversation_id),
                    sender_id=message_action.data.sender_id,
                    recipient_id=message_action.data.recipient_id,
                    content=message_action.data.content,
                )
                await websocket.send_json(response)
            else:
                await websocket.send_json(error_response("Unknown action"))
                continue

        except HTTPException as he:
            await db.rollback()
            await websocket.send_json(error_response(he.detail))
            continue

        except WebSocketDisconnect:
            break

        except Exception as e:
            await db.rollback()
            logger.error(f"Unexpected error: {e}")
            await websocket.send_json(error_response("Unexpected server error."))
            break
