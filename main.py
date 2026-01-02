from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from google import genai
from PIL import Image
import io
from config import ALLOWED_TYPES, MAX_FILE_SIZE, GEMINI_API_KEY
from gemini_extract_and_explain import analyze_menu_image_gemini
from gemini_more_details import get_dish_details

# clients
app = FastAPI()
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# start backend: uvicorn main:app --reload
@app.get("/")
async def root():
    return {"message": "FastAPI initialized successfully!"}

@app.post("/details")
async def details(dish_context: str = File(...),
                 target_language: str = Form(...),
                  restaurant_name: str = Form(...)):
    try:
        result = get_dish_details(dish_context, target_language, restaurant_name, gemini_client)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Calling LLM error"
        )
    return result

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

    # 3. extract dish name and description by LLM
    result = analyze_menu_image_gemini(image_bytes, target_language, gemini_client)
    return result