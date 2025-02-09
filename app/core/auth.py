from functools import wraps
from fastapi import HTTPException, Request
from passlib.context import CryptContext
from app.crud import bot_info as bot_crud

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def require_admin_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request and bot_id directly from kwargs
        request = kwargs.get('request')
        bot_id = kwargs.get('bot_id')

        if not request:
            raise HTTPException(status_code=500, detail="Internal server error")

        admin_password = request.headers.get('admin-password')

        if not admin_password:
            raise HTTPException(status_code=401, detail="Admin password is required")

        if bot_id:
            # For update operations, verify against existing password
            bot_info = await bot_crud.get_bot_by_id(bot_id)
            if not bot_info or not verify_password(admin_password, bot_info.get('admin_password', '')):
                raise HTTPException(status_code=401, detail="Invalid admin password")

        return await func(*args, **kwargs)
    return wrapper