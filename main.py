from dotenv import load_dotenv
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from PIL import Image
import io
import easyocr
from langdetect import detect, LangDetectException
import numpy as np
from openai import OpenAI

from extract_dishname import extract_dish_names_llm_nano

# variables
OCR_LANGS_OTHER = [ 'en', 'fr', 'es']
TARGET_LANGS = {'en', 'zh', 'ja', 'fr', 'es'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please check your .env file.")

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
openai_client = OpenAI(api_key=api_key)

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
    joined_text = "\n".join(texts)
    try:
        source_language = detect(joined_text) if joined_text else "unknown"
    except LangDetectException:
        source_language = "unknown"
    if source_language not in OCR_LANGS_OTHER:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source language: {source_language}"
        )

    # 5. extract dishname only
    dish_names = extract_dish_names_llm_nano(openai_client, joined_text)
    dish_names = [dish for dish in dish_names if ',' not in dish]
    print("dish_names: ", dish_names)
    if (dish_names is None) or (len(dish_names) == 0):
        raise HTTPException(
            status_code=400,
            detail="Didn't find any dish names"
        )

    # 6. get explanation
    dish_text = "\n".join(dish_names)

    prompt = f"""
    For each dish name below, write ONE short explanation.

    Rules:
    - Output language: {target_language}
    - One sentence per dish. Simple and clear.
    - Return plain text, one description per line.

    Dish names:
    {dish_text}
    """

    print("final prompt: ", prompt)
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes menu item descriptions."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=300
    )
    print("response: ", response)
    description = response.choices[0].message.content
    print("description: ", description)

    lines = [line.strip() for line in response.choices[0].message.content.splitlines() if line.strip()]
    result = [{"name": name, "description": lines[i] if i < len(lines) else ""} for i, name in
              enumerate(dish_names)]

    return {
        "source_language": source_language,
        "target_language": target_language,
        "json_resp": result,
        "response": description
    }