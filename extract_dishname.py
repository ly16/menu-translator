import json
from openai import OpenAI

def extract_dish_names_llm_nano(client: OpenAI, menu_text: str):
    if not menu_text.strip():
        return []

    # 限制长度，防止 nano 被信息淹没
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
