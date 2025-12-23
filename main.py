from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from PIL import Image
import io
import easyocr
from openai import OpenAI
from config import OCR_LANGS_OTHER, OPENAI_API_KEY, TARGET_LANGS, ALLOWED_TYPES, MAX_FILE_SIZE
from explain_dish import get_dish_explanations
from extract_dishname import get_dish_names
from language_detect import detect_language
from ocr import extract_text_from_image_bytes

# clients
app = FastAPI()
# reader = easyocr.Reader(OCR_LANGS_OTHER)
# openai_client = OpenAI(api_key=OPENAI_API_KEY)

# start backend: uvicorn main:app --reload
@app.get("/")
async def root():
    return {"message": "FastAPI + Render successfully!"}

# @app.post("/upload")
# async def upload(file: UploadFile = File(...),
#                  target_language: str = Form(...)):
#     # 1. input validation
#     if target_language not in TARGET_LANGS:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Unsupported target language: {target_language}"
#         )
#     if file.content_type not in ALLOWED_TYPES:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Unsupported image format: {file.content_type}"
#         )
#
#     # 2. Upload image, image validation
#     image_bytes = await file.read()
#     if len(image_bytes) > MAX_FILE_SIZE:
#         raise HTTPException(
#             status_code=413,
#             detail="Image too large (max 5MB)"
#         )
#     try:
#         image = Image.open(io.BytesIO(image_bytes))
#         image.verify()
#     except Exception:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid image file"
#         )
#
#     # 3. Extract text: OCR
#     texts = extract_text_from_image_bytes(image_bytes, reader)
#
#     # 4. recognize source_language: OCR
#     joined_text = "\n".join(texts)
#     source_language = detect_language(joined_text)
#     if source_language == "unsupported":
#         raise HTTPException(
#             status_code=400,
#             detail=f"Unsupported source language: {source_language}"
#         )
#
#     # 5. extract dishname only
#     dish_names = get_dish_names(openai_client, joined_text)
#     if not dish_names:
#         raise HTTPException(
#             status_code=400,
#             detail="Didn't find any dish names"
#         )
#
#     # 6. get explanation
#     result = get_dish_explanations(openai_client, dish_names, target_language)
#
#     return {
#         "source_language": source_language,
#         "target_language": target_language,
#         "json_resp": result,
#     }