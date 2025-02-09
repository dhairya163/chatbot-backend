import pytest
import motor.motor_asyncio
from typing import AsyncGenerator
from datetime import datetime
from app.crud.bot_info import BotInfoCRUD
from app.crud.chat import ChatCRUD
from app.models.conversation import MessageType

@pytest.fixture
async def test_db() -> AsyncGenerator:
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_chatbot_db"]
    yield db
    await client.drop_database("test_chatbot_db")
    client.close()

@pytest.fixture
async def bot_crud(test_db) -> BotInfoCRUD:
    return BotInfoCRUD(test_db)

@pytest.fixture
async def chat_crud(test_db) -> ChatCRUD:
    return ChatCRUD(test_db)

@pytest.fixture
def sample_bot_data():
    return {
        "headline": "Hello, I'm Test Bot",
        "starter_message": {
            "message": "Welcome! I'm here to help answer your questions and provide assistance. How can I help you today?",
            "action_items": ["Learn about our services", "Get support"]
        },
        "secondary_description": "Test Bot is an AI chatbot that helps in resolving customer support queries. This bot is available for testing purposes.",
        "logo": "https://example.com/test-bot-logo.png",
        "admin_password": "12345678",
        "created_at": datetime.utcnow()
    }

@pytest.fixture
def sample_message_data():
    return {
        "message_id": "test_msg_1",
        "type": MessageType.USER,
        "message": "Hello, bot!",
        "is_deleted": False,
        "versions": []
    }