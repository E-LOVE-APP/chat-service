from pydantic import BaseModel, Field


class SendMessageData(BaseModel):
    """
    The payload containing details needed to send a new message within a conversation.
    """

    sender_id: str = Field(..., description="UUID string of the message sender.")
    recipient_id: str = Field(..., description="UUID string of the message recipient.")
    content: str = Field(..., description="The text content of the message.")


class SendMessageAction(BaseModel):
    """
    The expected structure of a WebSocket message when sending a new message.

    The client should send:
    {
      "action": "send_message",
      "data": {
        "sender_id": "<uuid-string>",
        "recipient_id": "<uuid-string>",
        "content": "<message-text>"
      }
    }
    """

    # TODO: put in ENUM?
    action: str = Field(..., description="The action type, expected 'send_message'.")
    data: SendMessageData = Field(..., description="The payload for the message to send.")
