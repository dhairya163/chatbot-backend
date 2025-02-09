import pytest
from app.models.conversation import BotConversation, Message
from datetime import datetime

pytestmark = pytest.mark.asyncio

@pytest.fixture
def sample_conversation(sample_message_data):
    return BotConversation(
        chat_id="test_chat_1",
        bot_id="test_bot_1",
        user_id="test_user_1",
        messages=[Message(**sample_message_data)],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

async def test_create_conversation(chat_crud, sample_conversation):
    # Test creating a new conversation
    created_conv = await chat_crud.create_conversation(sample_conversation)
    assert created_conv is not None
    assert created_conv.chat_id == sample_conversation.chat_id
    assert created_conv.bot_id == sample_conversation.bot_id
    assert len(created_conv.messages) == 1

async def test_get_conversation(chat_crud, sample_conversation):
    # Create a conversation first
    await chat_crud.create_conversation(sample_conversation)
    
    # Test retrieving the conversation
    retrieved_conv = await chat_crud.get_conversation(sample_conversation.chat_id)
    assert retrieved_conv is not None
    assert retrieved_conv.chat_id == sample_conversation.chat_id
    assert retrieved_conv.bot_id == sample_conversation.bot_id
    
    # Test retrieving non-existent conversation
    non_existent = await chat_crud.get_conversation("non_existent_chat")
    assert non_existent is None

async def test_get_chat_history(chat_crud, sample_conversation):
    # Create a conversation first
    await chat_crud.create_conversation(sample_conversation)
    
    # Test retrieving chat history
    history = await chat_crud.get_chat_history(
        sample_conversation.chat_id,
        sample_conversation.bot_id
    )
    assert history is not None
    assert history.chat_id == sample_conversation.chat_id
    assert history.bot_id == sample_conversation.bot_id
    assert len(history.messages) == 1

async def test_add_message(chat_crud, sample_conversation, sample_message_data):
    # Create a conversation first
    await chat_crud.create_conversation(sample_conversation)
    
    # Create a new message
    new_message = Message(
        **{**sample_message_data,
           "message_id": "test_msg_2",
           "message": "How are you?"}
    )
    
    # Test adding a message
    success = await chat_crud.add_message(sample_conversation.chat_id, new_message)
    assert success is True
    
    # Verify message was added
    updated_conv = await chat_crud.get_conversation(sample_conversation.chat_id)
    assert len(updated_conv.messages) == 2
    assert updated_conv.messages[-1].message == "How are you?"

async def test_update_message(chat_crud, sample_conversation):
    # Create a conversation first
    await chat_crud.create_conversation(sample_conversation)
    
    # Test updating a message
    updated_text = "Updated message text"
    success = await chat_crud.update_message(
        sample_conversation.chat_id,
        sample_conversation.messages[0].message_id,
        updated_text
    )
    assert success is True
    
    # Verify message was updated
    updated_conv = await chat_crud.get_conversation(sample_conversation.chat_id)
    assert updated_conv.messages[0].message == updated_text
    assert updated_text in updated_conv.messages[0].versions

async def test_delete_message(chat_crud, sample_conversation):
    # Create a conversation first
    await chat_crud.create_conversation(sample_conversation)
    
    # Test deleting a message
    success = await chat_crud.delete_message(
        sample_conversation.chat_id,
        sample_conversation.messages[0].message_id
    )
    assert success is True
    
    # Verify message was marked as deleted
    updated_conv = await chat_crud.get_conversation(sample_conversation.chat_id)
    assert updated_conv.messages[0].is_deleted is True 