from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from PIL import Image
import io
from config import ALLOWED_TYPES, MAX_FILE_SIZE
from gemini_extract_and_explain import analyze_menu_image_gemini

# clients
app = FastAPI()

# start backend: uvicorn main:app --reload
@app.get("/")
async def root():
    return {"message": "FastAPI initialized successfully!"}

@app.post("/upload")
async def upload(file: UploadFile = File(...),
                 target_language: str = Form(...)):
    # 1. input validation
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

    # 3. extract dishname and description by LLM
    result = analyze_menu_image_gemini(image_bytes, target_language)
    return result