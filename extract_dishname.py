import json
from openai import OpenAI

def get_dish_names(openai_client: OpenAI, text: str):
    dish_names = extract_dish_names_llm_nano(openai_client, text)
    # remove items with commas if needed
    dish_names = [dish for dish in dish_names if ',' not in dish]
    return dish_names

def extract_dish_names_llm_nano(client: OpenAI, menu_text: str):
    if not menu_text.strip():
        return []
    menu_text = menu_text[:1500]

    prompt = f"""
From the text below, extract ONLY the dish names (the food items that can be ordered).
- Ignore prices, wine names, drinks, notes, categories.
- no comma in between.
- Output ONLY a JSON array of strings.
- Do NOT translate or explain.
- Each dish name should be as it appears in the text.

Text:
{menu_text}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=300
    )

    content = response.choices[0].message.content.strip()
    try:
        dishes = json.loads(content)
        if isinstance(dishes, list):
            return [str(d) for d in dishes if d]
    except Exception:
        pass
    lines = menu_text.splitlines()
    fallback = [line for line in lines if line.isupper()][:10]
    return fallback
