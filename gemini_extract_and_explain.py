from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from config import GEMINI_API_KEY


client = genai.Client(api_key=GEMINI_API_KEY)
class MenuItem(BaseModel):
    source_name: str = Field(description="The exact dish name as written on the menu")
    translation: str = Field(description="The name translated to target language + a short appetizing description")

class MenuResponse(BaseModel):
    items: List[MenuItem]


def analyze_menu_image_gemini(image_bytes: bytes, target_language: str) -> List[dict]:
    # 1. Prepare the Prompt
    prompt_text = f"""
    Analyze this menu image strictly. 
    Target Language for description: {target_language}.

    For every dish found:
    1. Extract the exact text name from the image.
    2. Extract the (optional) recipients name from the image and description based on recipients.
    2. Translate it and write a short, 1-sentence appetizing description.

    Ignore non-food text like phone numbers or addresses.
    """

    # 2. Call Gemini 2.0 Flash
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # Use this exact string
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt_text
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MenuResponse,
            temperature=0.1
        )
    )

    # 3. Automatic Parsing
    try:
        # parsed returns the 'MenuResponse' instance
        menu_data = response.parsed
        if not menu_data or not menu_data.items:
            return []
        return [item.model_dump() for item in menu_data.items]

    except Exception as e:
        print(f"Gemini Parsing Error: {e}")
        return []