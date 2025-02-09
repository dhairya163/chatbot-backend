from fastapi import APIRouter

from app.api.bot_info import router as bot_router
from app.api.chat import router as chat_router

api_router = APIRouter()

api_router.include_router(bot_router)
api_router.include_router(chat_router)
