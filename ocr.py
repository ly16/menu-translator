from PIL import Image
import io
import numpy as np
import easyocr


def extract_text_from_image_bytes(
    image_bytes: bytes,
    reader: easyocr.Reader,
    min_confidence: float = 0.4
) -> list[str]:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)
    ocr_result = reader.readtext(image_np)
    texts = [
        text
        for _, text, conf in ocr_result
        if conf >= min_confidence
    ]

    return texts
