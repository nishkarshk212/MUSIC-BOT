import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Logging configuration
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)

# Message deletion time options (in seconds)
TIME_OPTIONS = {
    '10s': 10,
    '30s': 30,
    '1m': 60,
    '5m': 300,
    '10m': 600,
    '30m': 1800,
    '1h': 3600,
    'off': 0
}

# Default deletion time (30 seconds)
DEFAULT_TIME = 30

# Message storage (in production, use database)
message_timers = {}  # {message_id: (chat_id, delete_time)}

# Custom timer storage for each user
user_custom_timers = {}  # {user_id: {'hours': int, 'minutes': int, 'seconds': int}}