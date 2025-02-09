from bson import ObjectId
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.bot_info import BotInfo

class BotInfoCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[BotInfo.Config.collection_name]

    async def get_bot_by_id(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve bot information by ID from the database
        """
        return await self.collection.find_one({"_id": ObjectId(bot_id)})

    async def update_bot_info(self, bot_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update bot information in the database
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(bot_id)},
            {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_bot_by_id(bot_id)
        return None

    async def create_bot_info(self, bot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new bot information in the database
        """
        result = await self.collection.insert_one(bot_data)
        return await self.get_bot_by_id(str(result.inserted_id))

    async def delete_bot_info(self, bot_id: str) -> bool:
        """
        Delete bot information from the database
        """
        result = await self.collection.delete_one({"_id": ObjectId(bot_id)})
        return result.deleted_count > 0

    async def get_all_bots(self) -> List[Dict[str, Any]]:
        """
        Retrieve all bots from the database
        """
        cursor = self.collection.find({})
        return await cursor.to_list(length=None) 