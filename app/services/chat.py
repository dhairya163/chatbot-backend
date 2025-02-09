import uuid
from typing import AsyncGenerator, Tuple, Optional, List
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.config import settings
from openai import AsyncOpenAI
from app.core.logger import logger
from app.core.constants import NO_BOT_DESCRIPTION, SYSTEM_MESSAGE_TEMPLATE, THIS_MESSAGE_WAS_DELETED

from app.crud.bot_info import BotInfoCRUD
from app.crud.chat import ChatCRUD
from app.models.conversation import Message, MessageType, BotConversation
from app.schemas.chat import (
    MessageCreate, 
    MessageResponse, 
    StreamResponse, 
    CompletionResponse,
    ChatHistory,
    HistoryMessage,
    MessageEdit
)

class ChatService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.bot_info_curd = BotInfoCRUD(db)
        self.crud = ChatCRUD(db)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_chat_history(self, chat_id: str, bot_id: str) -> ChatHistory:
        conversation = await self.crud.get_chat_history(chat_id, bot_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        return ChatHistory(
            chat_id=conversation.chat_id,
            bot_id=conversation.bot_id,
            messages=[
                HistoryMessage(
                    message_id=msg.message_id,
                    type=msg.type,
                    message=msg.message,
                    versions=msg.versions,
                    is_deleted=msg.is_deleted
                ) for msg in conversation.messages
            ]
        )

    async def edit_message(self, edit_data: MessageEdit) -> ChatHistory:
        # Get conversation
        conversation = await self.crud.get_chat_history(edit_data.chat_id, edit_data.bot_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # If updating message
        if edit_data.updated_value is not None:
            success = await self.crud.update_message(
                edit_data.chat_id,
                edit_data.message_id,
                edit_data.updated_value
            )
        # If deleting message
        elif edit_data.is_delete:
            success = await self.crud.delete_message(
                edit_data.chat_id,
                edit_data.message_id
            )
        else:
            raise HTTPException(status_code=400, detail="Either updated_value or is_delete must be provided")

        if not success:
            raise HTTPException(status_code=404, detail="Message not found")

        # Get updated conversation
        updated_conversation = await self.crud.get_chat_history(edit_data.chat_id, edit_data.bot_id)
        return ChatHistory(
            chat_id=updated_conversation.chat_id,
            bot_id=updated_conversation.bot_id,
            messages=[
                HistoryMessage(
                    message_id=msg.message_id,
                    type=msg.type,
                    message=msg.message,
                    versions=msg.versions,
                    is_deleted=msg.is_deleted
                ) for msg in updated_conversation.messages
            ]
        )

    def _build_message_history(self, conversation: BotConversation) -> List[dict]:
        messages = []
        for msg in conversation.messages:
            if msg.is_deleted:
                messages.append({"role": msg.type, "content": THIS_MESSAGE_WAS_DELETED})
            role = "assistant" if msg.type == MessageType.ASSISTANT else "user"
            messages.append({"role": role, "content": msg.message})
        return messages
    
    async def create_system_message(self, bot_id: str) -> str:
        bot_info = await self.bot_info_curd.get_bot_by_id(bot_id=bot_id)
        return SYSTEM_MESSAGE_TEMPLATE.format(bot_description=bot_info.get("secondary_description", NO_BOT_DESCRIPTION))

    async def call_openai(self, conversation: BotConversation, user_message: str) -> AsyncGenerator:
        messages = []
        messages.append({
            "role": "system", 
            "content": await self.create_system_message(conversation.bot_id)
        })
        messages.extend(self._build_message_history(conversation))
        messages.append({"role": "user", "content": user_message})
        return await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True
        )

    async def process_message(
        self,
        message_data: MessageCreate,
    ) -> AsyncGenerator[Tuple[str, dict], None]:
        # Generate message IDs
        user_message_id = str(uuid.uuid4())
        assistant_message_id = str(uuid.uuid4())

        # Create user message
        user_message = Message(
            message_id=user_message_id,
            type=MessageType.USER,
            message=message_data.message,
            versions=[message_data.message]
        )

        # Initialize assistant message
        assistant_message = Message(
            message_id=assistant_message_id,
            type=MessageType.ASSISTANT,
            message=""
        )

        # Get or create conversation
        conversation = await self.crud.get_conversation(message_data.chat_id)
        if not conversation:
            conversation = BotConversation(
                chat_id=message_data.chat_id,
                bot_id=message_data.bot_id,
                messages=[]
            )
            await self.crud.create_conversation(conversation)

        # Send user message confirmation
        user_response = MessageResponse(
            message_id=user_message_id,
            type=MessageType.USER,
            message=message_data.message
        )
        yield "user_message", user_response.dict()

        # Stream the chat completion
        buffer = ""
        try:
            stream = await self.call_openai(conversation, message_data.message)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    buffer += delta
                    stream_response = StreamResponse(
                        message_id=assistant_message_id,
                        delta=delta,
                        buffer=buffer
                    )
                    yield "assistant_message", stream_response.dict()

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
            # If an error occurs, yield an assistant message with a failure notice
            error_message = "AI call failed"
            stream_response = StreamResponse(
                message_id=assistant_message_id,
                delta=error_message,
                buffer=buffer + error_message
            )
            yield "assistant_message", stream_response.dict()
            
        # Update assistant message with complete response
        assistant_message.message = buffer

        # Save both messages together in a single database call
        if not await self.crud.add_messages(message_data.chat_id, [user_message, assistant_message]):
            raise HTTPException(status_code=500, detail="Failed to save messages")

        # Send completion confirmation
        completion = CompletionResponse(message_id=assistant_message_id)
        yield "done", completion.dict()