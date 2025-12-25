import os
from dotenv import load_dotenv

# constants
SOURCE_LANG_MAP = {
    "Simplified Chinese": "chi_sim",
    "Traditional Chinese": "chi_tra",
    "English": "eng",
    "Japanese": "jpn",
    "French": "fra",
    "Spanish": "spa",
    "Italian": "ita",
    "Korean": "kor"
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
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY")
if not OCR_SPACE_API_KEY:
    raise ValueError("OCR_SPACE_API_KEY not found. Please check your .env file.")
