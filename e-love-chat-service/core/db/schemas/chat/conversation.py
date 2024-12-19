from typing import Optional

from pydantic import BaseModel, Field


class CreateConversationRequest(BaseModel):
    """
    Request body model for creating a new conversation between two users.

    This model defines the input structure for the POST /conversations endpoint.
    Both user_first_id and user_second_id should be valid UUID strings
    (they can remain as strings if the database stores them as VARCHAR(36)).
    """

    user_first_id: str = Field(
        ..., description="The UUID string of the first user in the conversation."
    )
    user_second_id: str = Field(
        ..., description="The UUID string of the second user in the conversation."
    )


class CreateConversationOutput(BaseModel):
    """
    Output model returned after successfully creating a conversation.

    This model defines the response structure for the POST /conversations endpoint.
    All fields are strings representing UUIDs, to avoid explicit conversions
    in the endpoint code.
    """

    id: str = Field(..., description="The UUID string of the created conversation.")
    user_first_id: str = Field(..., description="The UUID string of the first user.")
    user_second_id: str = Field(..., description="The UUID string of the second user.")


class SendMessageData(BaseModel):
    """
    Payload model containing the details needed to send a message within a conversation.

    This model is nested inside SendMessageAction and represents the 'data' field of
    the incoming WebSocket JSON when 'action' is 'send_message'.
    """

    sender_id: str = Field(..., description="The UUID string of the user sending the message.")
    recipient_id: str = Field(..., description="The UUID string of the user receiving the message.")
    content: str = Field(..., description="The text content of the message.")


class SendMessageAction(BaseModel):
    """
    Model defining the expected structure of the WebSocket message when sending a message.

    Clients should send JSON with "action": "send_message" and a "data" object
    containing sender_id, recipient_id, and content.
    """

    action: str = Field(..., description="The action type, expected to be 'send_message'.")
    data: SendMessageData = Field(
        ..., description="The message payload including sender_id, recipient_id, and content."
    )
