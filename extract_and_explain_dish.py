from openai import OpenAI
import re

def extract_and_explain_dishes(
    client: OpenAI,
    menu_text: str,
    target_language: str
):
    if not menu_text.strip():
        return ""

    menu_text = menu_text[:3000]

    system_prompt = """
    You are a professional restaurant menu translator and editor.
    You specialize in producing elegant, restaurant-quality dish descriptions.
    You never hallucinate or invent ingredients.
    You understand menu context and culinary terminology.
    """

    developer_prompt = f"""
    Task:
    You will receive OCR-extracted menu text with dish names and optional context (ingredients, preparation, etc.).
    For each dish:
    - Translate the dish name into the target language.
    - Write a rich, menu-style description in the target language.
    - Include when possible: texture, flavor, cooking method, dish positioning (starter, dessert, etc.).
    - Do not invent ingredients.
    - Keep original dish order.
    - Output format: <source_dish> | <target_dish> : <target_description>
    """

    user_prompt = f"""
    Target language: {target_language}

    Menu text:
    <<<
    {menu_text}
    >>>
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=400,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )


    unparsed = response.choices[0].message.content.strip()
    pattern = r"([A-Z\s]+)\s*\|\s*([^\n：:]+)[：:](.*?)(?=(?:\n[A-Z\s]+\s*\|)|$)"
    matches = re.findall(pattern, unparsed, re.DOTALL)
    parsed_result = []
    for source_name, target_name, description in matches:
        translation_text = f"{target_name.strip()}: {description.strip()}"
        parsed_result.append({
            "source_name": source_name.strip(),
            "translation": translation_text
        })

    return parsed_result

