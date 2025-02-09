from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from app.models.conversation import MessageType

class MessageCreate(BaseModel):
    chat_id: str
    bot_id: str
    message: str

class MessageEdit(BaseModel):
    chat_id: str
    bot_id: str
    message_id: str
    updated_value: Optional[str] = None
    is_delete: bool = False

class MessageResponse(BaseModel):
    message_id: str
    type: MessageType
    message: str
    status: str = "received"

class StreamResponse(BaseModel):
    message_id: str
    delta: str
    buffer: str

class CompletionResponse(BaseModel):
    message_id: str
    status: str = "completed"

class HistoryMessage(BaseModel):
    message_id: str
    type: MessageType
    message: str
    versions: List[str] = []
    is_deleted: bool = False

class ChatHistory(BaseModel):
    chat_id: str
    bot_id: str
    messages: List[HistoryMessage] = [] 