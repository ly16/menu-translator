from langdetect import detect, LangDetectException
from config import OCR_LANGS_OTHER

def detect_language(text: str) -> str:
    try:
        lang = detect(text) if text else "unknown"
    except LangDetectException:
        lang = "unknown"
    if lang not in OCR_LANGS_OTHER:
        return "unsupported"
    return lang
