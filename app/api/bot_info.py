from fastapi import APIRouter, Request, HTTPException, Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.bot import BotInfoResponse, BotInfoCreate, BotInfoUpdate, BotInfoListResponse
from app.services.bot_info import BotInfoService
from app.core.auth import require_admin_auth
from app.database.mongodb import get_database

router = APIRouter(
    prefix="/bot",
    tags=["bot"]
)

@router.get("", response_model=List[BotInfoListResponse])
async def list_bots(db: AsyncIOMotorDatabase = Depends(get_database)):
    service = BotInfoService(db)
    return await service.list_bots()

@router.get("/{bot_id}", response_model=BotInfoResponse)
@require_admin_auth
async def get_bot_info(
    bot_id: str, 
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    try:
        service = BotInfoService(db)
        return await service.get_bot_info(bot_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("", response_model=BotInfoResponse)
async def create_bot_info(
    bot_data: BotInfoCreate, 
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    service = BotInfoService(db)
    return await service.create_bot_info(bot_data)

@router.put("/{bot_id}", response_model=BotInfoResponse)
@require_admin_auth
async def update_bot_info(
    bot_id: str, 
    bot_data: BotInfoUpdate, 
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    service = BotInfoService(db)
    return await service.update_bot_info(bot_id, bot_data)

@router.delete("/{bot_id}")
@require_admin_auth
async def delete_bot_info(
    bot_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    service = BotInfoService(db)
    return await service.delete_bot_info(bot_id)

