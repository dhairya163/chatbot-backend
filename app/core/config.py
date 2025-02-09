from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chatbot Backend"
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "chatbot_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 