from typing import List
import requests
from config import OCR_SPACE_API_KEY, SOURCE_LANG_MAP
from PIL import Image
import io

OCR_SPACE_API_URL = "https://api.ocr.space/parse/image"
MAX_IMAGE_SIZE = 1024 * 1024  # 1MB

def compress_image(image_bytes: bytes, quality: int) -> bytes:
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode in ("RGBA", "LA"):
        image = image.convert("RGB")
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def split_image(image_bytes: bytes, rows: int, cols: int) -> List[bytes]:
    image = Image.open(io.BytesIO(image_bytes))
    width, height = image.size
    block_bytes_list = []

    for r in range(rows):
        for c in range(cols):
            left = int(c * width / cols)
            upper = int(r * height / rows)
            right = int((c + 1) * width / cols)
            lower = int((r + 1) * height / rows)
            block = image.crop((left, upper, right, lower))
            if block.mode in ("RGBA", "LA"):
                block = block.convert("RGB")
            buf = io.BytesIO()
            block.save(buf, format="JPEG", quality=85)
            block_bytes_list.append(buf.getvalue())
    return block_bytes_list


def call_ocr_space(image_bytes: bytes, source_language: str) -> List[str]:
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


def extract_text_from_image_bytes(image_bytes: bytes, source_language: str) -> List[str]:
    # compress
    compressed_bytes = compress_image(image_bytes, quality=85)
    if len(compressed_bytes) <= MAX_IMAGE_SIZE:
        return call_ocr_space(compressed_bytes, source_language)

    # split and combine
    blocks = split_image(image_bytes, rows=2, cols=1)
    all_texts = []
    for block in blocks:
        try:
            block_texts = call_ocr_space(block, source_language)
            all_texts.extend(block_texts)
        except Exception as e:
            print("OCR block failed:", e)
            continue
    # combine
    all_texts = list(dict.fromkeys(all_texts))
    all_texts = [t for t in all_texts if t]
    return all_texts
