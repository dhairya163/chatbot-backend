# OpenAI related constants
SYSTEM_MESSAGE_TEMPLATE = """
You are a helpful AI assistant. Provide clear, accurate, and engaging responses. 
Based on the user's message and description of the bot, provide a response that is relevant to the user's message and the bot's description.
Try to reply in 50-60 words or less, unless required to reply in more words.
Bot Description: 
{bot_description}
"""

THIS_MESSAGE_WAS_DELETED = "This message was deleted"
NO_BOT_DESCRIPTION = "No bot description provided"

# Logging related constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE_MAX_BYTES = 10485760  # 10MB
LOG_FILE_BACKUP_COUNT = 5 