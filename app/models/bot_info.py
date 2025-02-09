from typing import Optional, List
from pydantic import Field

from app.models.base import MongoBaseModel

class WelcomeMessage(MongoBaseModel):
    message: str = Field(..., description="The text content of the welcome message")
    action_items: List[str] = Field(..., description="List of action items or suggestions for the user")

class BotInfo(MongoBaseModel):
    headline: str = Field(..., description="The main headline/title of the bot")
    starter_message: WelcomeMessage = Field(..., description="The initial welcome message and action items shown to users")
    secondary_description: Optional[str] = Field(None, description="Additional description or details about the bot")
    logo: Optional[str] = Field(None, description="URL or path to the bot's logo image")

    class Config:
        collection_name = "bot_info" 