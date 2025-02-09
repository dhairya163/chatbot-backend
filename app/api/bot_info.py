from fastapi import APIRouter, Request, HTTPException
from typing import List
from app.schemas.bot import BotInfoResponse, BotInfoCreate, BotInfoUpdate, BotInfoListResponse
from app.services import bot_info as bot_service
from app.core.auth import require_admin_auth

router = APIRouter(
    prefix="/bot",
    tags=["bot"]
)

@router.get("", response_model=List[BotInfoListResponse])
async def list_bots():
    return await bot_service.list_bots()

@router.get("/{bot_id}", response_model=BotInfoResponse)
@require_admin_auth
async def get_bot_info(bot_id: str, request: Request):
    try:
        return await bot_service.get_bot_info(bot_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("", response_model=BotInfoResponse)
async def create_bot_info(bot_data: BotInfoCreate, request: Request):
    return await bot_service.create_bot_info(bot_data)

@router.put("/{bot_id}", response_model=BotInfoResponse)
@require_admin_auth
async def update_bot_info(bot_id: str, bot_data: BotInfoUpdate, request: Request):
    return await bot_service.update_bot_info(bot_id, bot_data)

