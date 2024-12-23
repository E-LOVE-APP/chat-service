from typing import Dict


def message_saved_response(sender_id: str, recipient_id: str, content: str) -> Dict:
    """
    Returns a JSON-compatible dict representing a successful 'message_saved' action response.
    """
    return {
        "action": "message_saved",
        "data": {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": content,
        },
    }


def error_response(error_detail: str) -> Dict:
    """
    Returns a JSON-compatible dict for error messages.
    """
    return {"error": error_detail}
