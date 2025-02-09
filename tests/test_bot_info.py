import pytest
from bson import ObjectId
from datetime import datetime

pytestmark = pytest.mark.asyncio

async def test_create_bot_info(bot_crud, sample_bot_data):
    # Test creating a new bot
    created_bot = await bot_crud.create_bot_info(sample_bot_data)
    assert created_bot is not None
    assert created_bot["headline"] == sample_bot_data["headline"]
    assert created_bot["secondary_description"] == sample_bot_data["secondary_description"]
    assert created_bot["starter_message"]["message"] == sample_bot_data["starter_message"]["message"]
    assert "_id" in created_bot

async def test_get_bot_by_id(bot_crud, sample_bot_data):
    # Create a bot first
    created_bot = await bot_crud.create_bot_info(sample_bot_data)
    bot_id = str(created_bot["_id"])
    
    # Test retrieving the bot
    retrieved_bot = await bot_crud.get_bot_by_id(bot_id)
    assert retrieved_bot is not None
    assert retrieved_bot["headline"] == sample_bot_data["headline"]
    
    # Test retrieving non-existent bot
    non_existent = await bot_crud.get_bot_by_id(str(ObjectId()))
    assert non_existent is None

async def test_update_bot_info(bot_crud, sample_bot_data):
    # Create a bot first
    created_bot = await bot_crud.create_bot_info(sample_bot_data)
    bot_id = str(created_bot["_id"])
    
    # Update bot info
    update_data = {
        "headline": "Updated Bot Headline",
        "starter_message": {
            "message": "Updated welcome message",
            "action_items": ["Updated action"]
        }
    }
    updated_bot = await bot_crud.update_bot_info(bot_id, update_data)
    
    assert updated_bot is not None
    assert updated_bot["headline"] == "Updated Bot Headline"
    assert updated_bot["starter_message"]["message"] == "Updated welcome message"
    assert updated_bot["secondary_description"] == sample_bot_data["secondary_description"]

async def test_delete_bot_info(bot_crud, sample_bot_data):
    # Create a bot first
    created_bot = await bot_crud.create_bot_info(sample_bot_data)
    bot_id = str(created_bot["_id"])
    
    # Test deleting the bot
    deleted = await bot_crud.delete_bot_info(bot_id)
    assert deleted is True
    
    # Verify bot is deleted
    retrieved_bot = await bot_crud.get_bot_by_id(bot_id)
    assert retrieved_bot is None
    
    # Test deleting non-existent bot
    deleted = await bot_crud.delete_bot_info(str(ObjectId()))
    assert deleted is False

async def test_get_all_bots(bot_crud, sample_bot_data):
    # Create first bot
    first_bot = await bot_crud.create_bot_info(sample_bot_data)
    
    # Create second bot with different data
    second_bot_data = sample_bot_data.copy()
    if "_id" in second_bot_data:
        del second_bot_data["_id"]  # Remove _id if present
    second_bot_data["headline"] = "Hello, I'm Second Bot"
    await bot_crud.create_bot_info(second_bot_data)
    
    # Test retrieving all bots
    all_bots = await bot_crud.get_all_bots()
    assert len(all_bots) == 2
    assert any(bot["headline"] == sample_bot_data["headline"] for bot in all_bots)
    assert any(bot["headline"] == "Hello, I'm Second Bot" for bot in all_bots) 