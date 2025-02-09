import uuid
from typing import AsyncGenerator, Tuple, Optional
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

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
        self.crud = ChatCRUD(db)

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

        # TODO: Replace this with actual chat processing logic
        response_text = f"Echo: {message_data.message}"
        buffer = ""

        # Stream assistant response
        for char in response_text:
            buffer += char
            stream_response = StreamResponse(
                message_id=assistant_message_id,
                delta=char,
                buffer=buffer
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