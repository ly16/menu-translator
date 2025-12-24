from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from PIL import Image
import io
from config import ALLOWED_TYPES, MAX_FILE_SIZE, SOURCE_LANG_MAP
from extract_and_explain_dish import extract_and_explain_dishes
from ocr import extract_text_from_image_bytes
from utils import get_reader, get_openai_client

# clients
app = FastAPI()

# start backend: uvicorn main:app --reload
@app.get("/")
async def root():
    return {"message": "FastAPI initialized successfully!"}

@app.post("/upload")
async def upload(file: UploadFile = File(...),
                 source_language: str = Form(...),
                 target_language: str = Form(...)):
    # 1. input validation
    if source_language not in SOURCE_LANG_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source language: {source_language}"
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
    reader = get_reader(source_language)
    texts = extract_text_from_image_bytes(image_bytes, reader)

    # 4. extract dishname and description by LLM
    joined_text = "\n".join(texts)
    openai_client = get_openai_client()
    result = extract_and_explain_dishes(openai_client, joined_text, target_language)

    return result