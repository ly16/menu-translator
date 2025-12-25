from openai import OpenAI

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
    - Write a rich, menu-style one sentence description in the target language.
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
        max_tokens=600,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )


    unparsed = response.choices[0].message.content.strip()
    return parse_menu_to_json(unparsed)

def parse_menu_to_json(text: str):
    result = []

    for line in text.strip().splitlines():
        parts = [p.strip() for p in line.split("|", 1)]
        if len(parts) != 2:
            continue
        source_name, translation = parts
        result.append({
            "source_name": source_name,
            "translation": translation
        })

    return result

