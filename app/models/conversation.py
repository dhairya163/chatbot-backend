from typing import List, Optional
from pydantic import Field
from enum import Enum

from app.models.base import MongoBaseModel

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(MongoBaseModel):
    message_id: str = Field(..., description="Unique identifier for the message")
    type: MessageType = Field(..., description="Type of message - user or assistant")
    message: str = Field(..., description="Content of the message")
    versions: List[str] = Field(default_factory=list, description="Array of message versions for edit history")
    is_deleted: bool = Field(default=False, description="Flag to mark if message is deleted")

class BotConversation(MongoBaseModel):
    chat_id: str = Field(..., description="Unique identifier for the chat")
    bot_id: str = Field(..., description="Identifier of the bot")
    messages: List[Message] = Field(default_factory=list, description="List of messages in the conversation")

    class Config:
        collection_name = "bot_conversations" 