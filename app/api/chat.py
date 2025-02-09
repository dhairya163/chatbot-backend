from fastapi import APIRouter, Request, Depends
from sse_starlette.sse import EventSourceResponse
import json
import asyncio

from app.database.mongodb import get_database
from app.crud.chat import ChatCRUD
from app.services.chat import ChatService
from app.schemas.chat import (
    MessageCreate, 
    MessageResponse, 
    StreamResponse, 
    CompletionResponse,
    ChatHistory,
    HistoryMessage,
    MessageEdit
)

router = APIRouter(prefix="/chat")

@router.get("/history")
async def get_chat_history(
    chat_id: str,
    bot_id: str,
    db=Depends(get_database)
) -> ChatHistory:
    crud = ChatCRUD(db)
    service = ChatService(crud)
    return await service.get_chat_history(chat_id, bot_id)

@router.put("/message")
async def edit_message(
    edit_data: MessageEdit,
    db=Depends(get_database)
) -> ChatHistory:
    crud = ChatCRUD(db)
    service = ChatService(crud)
    return await service.edit_message(edit_data)

@router.post("/sse")
async def chat_endpoint(
    request: Request,
    message_data: MessageCreate,
    db=Depends(get_database)
):
    async def event_generator():
        crud = ChatCRUD(db)
        service = ChatService(crud)
        
        async for event_type, data in service.process_message(message_data):
            if await request.is_disconnected():
                break
                
            yield {
                "event": event_type,
                "data": json.dumps(data)
            }
            
            # Add small delay for streaming effect
            if event_type == "assistant_message":
                await asyncio.sleep(0.1)

    return EventSourceResponse(event_generator()) 