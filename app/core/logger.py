import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.constants import LOG_FORMAT, LOG_FILE_MAX_BYTES, LOG_FILE_BACKUP_COUNT

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logger = logging.getLogger("chatbot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter(LOG_FORMAT)
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# File handler
file_handler = RotatingFileHandler(
    logs_dir / "chatbot.log",
    maxBytes=LOG_FILE_MAX_BYTES,
    backupCount=LOG_FILE_BACKUP_COUNT
)
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Prevent the logger from propagating to the root logger
logger.propagate = False 