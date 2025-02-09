from typing import Optional, List
from pydantic import BaseModel, SecretStr
from datetime import datetime

class WelcomeMessage(BaseModel):
    message: str
    action_items: List[str]

class BotInfoBase(BaseModel):
    headline: str
    starter_message: WelcomeMessage
    secondary_description: Optional[str] = None
    logo: Optional[str] = None

class BotInfoCreate(BotInfoBase):
    admin_password: str

class BotInfoUpdate(BaseModel):
    headline: Optional[str] = None
    starter_message: Optional[WelcomeMessage] = None
    secondary_description: Optional[str] = None
    logo: Optional[str] = None

class BotInfoResponse(BotInfoBase):
    id: str
    created_at: datetime

class BotInfoListResponse(BaseModel):
    id: str
    headline: str
    logo: Optional[str] = None
    created_at: datetime 