import os

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Similarity Configuration
SIMILARITY_THRESHOLD = 0.77  # 77% similarity threshold (75-85% range)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Command Configuration
COMMAND_AUTO_DELETE_SECONDS = 60  # Delete admin commands after 60 seconds

# Database Configuration
DATABASE_PATH = "spam_db.sqlite"

# Emoji Configuration
SPAM_FLAG_EMOJI = "👎"  # Thumbs down emoji for repeat spam
