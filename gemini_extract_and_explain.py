from typing import List
from google import genai
from google.genai import types

def analyze_menu_image_gemini(image_bytes: bytes, target_language: str, client: genai.Client) -> List[dict]:
    prompt_text = f"""
    Analyze this menu image strictly. 
    Target Language: {target_language}.

    For every dish found:
    1. Extract the exact dish name from the image.
    2. Identify ingredients or cooking methods mentioned in the image for that dish.
    3. Translate the name and write a 1-sentence appetizing description in {target_language}.
       - Use the identified ingredients to make the description specific and enticing.
       - If no ingredients are listed, describe the dish's typical flavor profile.
    4. A list of exactly 2 tags in {target_language}. 
       - Tag 1: Dietary/Status (e.g., "Vegetarian", "Chef's Choice").
       - Tag 2: Sensory/Style (e.g., "Seasonal", "Crispy").

    Format each item as: source_name ## translation ## tags

    Rules:
    - Use ONE line per item.
    - source_name: The exact dish name as written on the menu.
    - translation: "Translated Name:Appetizing description".
    - tags: use "," characters to separate tags.
    - Use exactly one "##" character as a separator, and DO NOT use the "##" characters anywhere else.
    - Do not include categories (like 'Appetizers'), prices, or contact info.
    """
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt_text
        ],
        config=types.GenerateContentConfig(
            response_mime_type="text/plain",
            temperature=0.1,
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL")
        )
    )

    menu_items = []
    try:
        raw_text = response.text
        if not raw_text:
            return []

        lines = raw_text.strip().split('\n')
        for line in lines:
            print("line: ", line)
            if "##" in line:
                parts = line.split("##", 2)
                menu_items.append({
                    "source_name": parts[0].strip(),
                    "translation": parts[1].strip(),
                    "tags" :  [tag.strip() for tag in parts[2].split(",")]
                })
        return menu_items

    except Exception as e:
        print(f"Error during parsing: {e}")
        return []