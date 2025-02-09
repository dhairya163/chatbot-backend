from bson import ObjectId
from typing import Optional, Dict, Any
from datetime import datetime

from app.database.mongodb import mongodb
from app.models.bot_info import BotInfo

async def get_bot_by_id(bot_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve bot information by ID from the database
    """
    return await mongodb.db[BotInfo.Config.collection_name].find_one({"_id": ObjectId(bot_id)})

async def update_bot_info(bot_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update bot information in the database
    """
    result = await mongodb.db[BotInfo.Config.collection_name].update_one(
        {"_id": ObjectId(bot_id)},
        {"$set": update_data}
    )
    if result.modified_count:
        return await get_bot_by_id(bot_id)
    return None

async def create_bot_info(bot_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create new bot information in the database
    """
    result = await mongodb.db[BotInfo.Config.collection_name].insert_one(bot_data)
    return await get_bot_by_id(str(result.inserted_id))

async def delete_bot_info(bot_id: str) -> bool:
    """
    Delete bot information from the database
    """
    result = await mongodb.db[BotInfo.Config.collection_name].delete_one({"_id": ObjectId(bot_id)})
    return result.deleted_count > 0

async def get_all_bots() -> list[Dict[str, Any]]:
    """
    Retrieve all bots from the database
    """
    cursor = mongodb.db[BotInfo.Config.collection_name].find({})
    return await cursor.to_list(length=None) 