from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.conversation import BotConversation, Message

class ChatCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[BotConversation.Config.collection_name]

    async def get_conversation(self, chat_id: str) -> Optional[BotConversation]:
        conversation_data = await self.collection.find_one({"chat_id": chat_id})
        if conversation_data:
            return BotConversation(**conversation_data)
        return None

    async def get_chat_history(self, chat_id: str, bot_id: str) -> Optional[BotConversation]:
        conversation_data = await self.collection.find_one(
            {
                "chat_id": chat_id,
                "bot_id": bot_id
            }
        )
        if conversation_data:
            return BotConversation(**conversation_data)
        return None

    async def create_conversation(self, conversation: BotConversation) -> BotConversation:
        await self.collection.insert_one(conversation.dict())
        return conversation

    async def add_messages(self, chat_id: str, messages: List[Message]) -> bool:
        result = await self.collection.update_one(
            {"chat_id": chat_id},
            {"$push": {"messages": {"$each": [msg.dict() for msg in messages]}}}
        )
        return result.modified_count > 0

    async def add_message(self, chat_id: str, message: Message) -> bool:
        result = await self.collection.update_one(
            {"chat_id": chat_id},
            {"$push": {"messages": message.dict()}}
        )
        return result.modified_count > 0

    async def update_message(self, chat_id: str, message_id: str, updated_message: str) -> bool:
        result = await self.collection.update_one(
            {
                "chat_id": chat_id,
                "messages.message_id": message_id
            },
            {
                "$set": {"messages.$.message": updated_message},
                "$push": {"messages.$.versions": updated_message}
            }
        )
        return result.modified_count > 0

    async def delete_message(self, chat_id: str, message_id: str) -> bool:
        result = await self.collection.update_one(
            {
                "chat_id": chat_id,
                "messages.message_id": message_id
            },
            {"$set": {"messages.$.is_deleted": True}}
        )
        return result.modified_count > 0 