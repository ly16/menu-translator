import os
from dotenv import load_dotenv

# constants
SOURCE_LANG_MAP = {
    "Simplified Chinese": "ch_sim",
    "Traditional Chinese": "ch_tra",
    "English": "en",
    "Japanese": "ja",
    "French": "fr",
    "Spanish": "es",
    "Italian": "it",
    "Korean": "ko"
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
# 👉 60–70% HEIC --> convert to JPEG in frontend
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

# OpenAI API key
if os.getenv("RENDER") != "true":
    load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Please check your .env file.")
