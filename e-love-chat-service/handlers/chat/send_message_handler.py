from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.services.conversations.conversations_service import ConversationsService
from core.services.message.message_service import MessagesService
from utils.chat.chat_responses import message_saved_response


async def handle_send_message(
    db: AsyncSession, conversation_id: str, sender_id: str, recipient_id: str, content: str
) -> dict:
    """
    Handle the 'send_message' action. (and anothers, potentially)
    Creates a new message in the specified conversation and returns the response payload.

    :param db: The database session.
    :param conversation_id: The UUID string of the conversation.
    :param sender_id: The UUID string of the sender.
    :param recipient_id: The UUID string of the recipient.
    :param content: The message content.
    :return: A dict representing the 'message_saved' response.
    :raises HTTPException: If message creation fails.
    """
    messages_service = MessagesService(db)
    # Note: conversations_service could be used here for additional checks if needed
    payload = {
        "conversation_id": conversation_id,
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "content": content,
    }

    new_message = await messages_service.create_message(payload)
    return message_saved_response(sender_id, recipient_id, content)
