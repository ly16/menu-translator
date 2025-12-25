from typing import List
import requests
from config import OCR_SPACE_API_KEY

OCR_SPACE_API_URL = "https://api.ocr.space/parse/image"

SOURCE_LANG_MAP = {
    "Simplified Chinese": "chs",
    "Traditional Chinese": "cht",
    "English": "eng",
    "Japanese": "jpn",
    "French": "fra",
    "Spanish": "spa",
    "Italian": "ita",
    "Korean": "kor"
}


def extract_text_from_image_bytes(
    image_bytes: bytes,
    source_language: str
) -> List[str]:

    lang_code = SOURCE_LANG_MAP.get(source_language, "eng")

    response = requests.post(
        OCR_SPACE_API_URL,
        files={"file": ("image.jpg", image_bytes)},
        data={
            "apikey": OCR_SPACE_API_KEY,
            "language": lang_code,
            "isOverlayRequired": "false"
        },
        timeout=30
    )

    if response.status_code != 200:
        raise RuntimeError(f"OCR.Space API request failed with status {response.status_code}")

    result = response.json()
    if result.get("IsErroredOnProcessing"):
        raise RuntimeError(f"OCR.Space API error: {result.get('ErrorMessage', 'Unknown error')}")

    texts = []
    for parsed_result in result.get("ParsedResults", []):
        raw_text = parsed_result.get("ParsedText", "")
        if not raw_text.strip():
            continue
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for line in lines:
            sub_parts = [part.strip() for part in line.split(",") if part.strip()]
            texts.extend(sub_parts)
    texts = list(dict.fromkeys(texts))
    texts = [t for t in texts if t]

    return texts
