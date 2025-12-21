from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from PIL import Image
import io
import easyocr
from langdetect import detect, LangDetectException
import numpy as np

# variables
OCR_LANGS_OTHER = [ 'en', 'fr', 'es']
TARGET_LANGS = {'en', 'zh', 'ja', 'fr', 'es'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
# 📱 iOS App：
# 👉 60–70% HEIC --> convert to JPEG in frontend
# 🌐 H5 Mobile Web：
# 👉 95% JPEG
# 🤖 Android App：
# 👉 90% JPEG
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

# clients
app = FastAPI()
reader = easyocr.Reader(OCR_LANGS_OTHER)

# start backend: uvicorn main:app --reload
@app.post("/upload")
async def upload(file: UploadFile = File(...),
                 target_language: str = Form(...)):
    # 1. input validation
    if target_language not in TARGET_LANGS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported target language: {target_language}"
        )
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format: {file.content_type}"
        )

    # 2. Upload image, image validation
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image too large (max 5MB)"
        )
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )

    # 3. Extract text: OCR
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)
    ocr_result = reader.readtext(image_np)
    texts = [text for _, text, conf in ocr_result if conf > 0.4]

    # 4. recognize source_language: OCR
    joined_text = " ".join(texts)
    try:
        source_language = detect(joined_text) if joined_text else "unknown"
    except LangDetectException:
        source_language = "unknown"
    if source_language not in OCR_LANGS_OTHER:
        raise HTTPException(
            status_code=400,
        )


    # 4. TODO: call openAI
    return {
        "filename": file.filename,
        "source_language": source_language,
        "target_language": target_language,
        "texts": texts
    }