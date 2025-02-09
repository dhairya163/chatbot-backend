from fastapi import HTTPException
from typing import Dict, Any
from datetime import datetime

from app.crud import bot_info as bot_crud
from app.schemas.bot import BotInfoResponse, BotInfoCreate, BotInfoUpdate, BotInfoListResponse
from app.core.auth import get_password_hash

async def get_bot_info(bot_id: str) -> BotInfoResponse:
    """
    Service function to get bot information
    Handles business logic and error cases
    """
    try:
        bot_info = await bot_crud.get_bot_by_id(bot_id)
        if bot_info is None:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Ensure starter_message has the correct structure
        starter_message = bot_info.get("starter_message", {})
        if not isinstance(starter_message, dict):
            starter_message = {}
            
        return BotInfoResponse(
            id=str(bot_info["_id"]),
            headline=bot_info.get("headline", ""),
            starter_message={
                "message": starter_message.get("message", ""),
                "action_items": starter_message.get("action_items", [])
            },
            secondary_description=bot_info.get("secondary_description"),
            logo=bot_info.get("logo"),
            created_at=bot_info.get("created_at", datetime.utcnow())
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bot: {str(e)}")

async def update_bot_info(bot_id: str, update_data: BotInfoUpdate) -> BotInfoResponse:
    """
    Service function to update bot information
    """
    try:
        bot_info = await bot_crud.update_bot_info(bot_id, update_data.model_dump(exclude_unset=True))
        if bot_info is None:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        starter_message = bot_info.get("starter_message", {})
        if not isinstance(starter_message, dict):
            starter_message = {}
            
        return BotInfoResponse(
            id=str(bot_info["_id"]),
            headline=bot_info.get("headline", ""),
            starter_message={
                "message": starter_message.get("message", ""),
                "action_items": starter_message.get("action_items", [])
            },
            secondary_description=bot_info.get("secondary_description"),
            logo=bot_info.get("logo"),
            created_at=bot_info.get("created_at", datetime.utcnow())
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating bot: {str(e)}")

async def create_bot_info(bot_data: BotInfoCreate) -> BotInfoResponse:
    """
    Service function to create new bot information
    """
    try:
        # Hash the password before storing
        data_dict = bot_data.model_dump()
        data_dict['admin_password'] = get_password_hash(data_dict['admin_password'])
        data_dict['created_at'] = datetime.utcnow()
        
        bot_info = await bot_crud.create_bot_info(data_dict)
        starter_message = bot_info.get("starter_message", {})
        if not isinstance(starter_message, dict):
            starter_message = {}
            
        return BotInfoResponse(
            id=str(bot_info["_id"]),
            headline=bot_info.get("headline", ""),
            starter_message={
                "message": starter_message.get("message", ""),
                "action_items": starter_message.get("action_items", [])
            },
            secondary_description=bot_info.get("secondary_description"),
            logo=bot_info.get("logo"),
            created_at=bot_info.get("created_at", datetime.utcnow())
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bot: {str(e)}")

async def delete_bot_info(bot_id: str) -> bool:
    """
    Service function to delete bot information
    """
    if not await bot_crud.delete_bot_info(bot_id):
        raise HTTPException(status_code=404, detail="Bot not found")
    return True

async def list_bots() -> list[BotInfoListResponse]:
    """
    Service function to list all bots with limited fields
    """
    try:
        bots = await bot_crud.get_all_bots()
        return [
            BotInfoListResponse(
                id=str(bot["_id"]),
                headline=bot.get("headline", ""),
                logo=bot.get("logo"),
                created_at=bot.get("created_at", datetime.utcnow())
            )
            for bot in bots
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing bots: {str(e)}") 