from openai import OpenAI

def get_dish_explanations(openai_client: OpenAI, dish_names: list[str], target_language: str):
    dish_text = "\n".join(dish_names)
    system_prompt = """
    You are a professional restaurant menu translator and editor.

    You specialize in translating and explaining food and dish names for menus.
    You always use standard culinary terminology commonly used in restaurant menus.
    You never translate food names by literal character meaning.
    You never hallucinate or invent ingredients.
    """

    developer_prompt = """
    Task:
    For each dish name provided, write ONE short menu-style description.

    Rules:
    - Output language must match the target language provided by the user
    - One sentence per dish
    - Return plain text only, one description per line
    - This is a restaurant menu description, not a dictionary translation
    - Include a brief, neutral description of the dish style or preparation
    - Description should include, when applicable:texture or mouth feel,cooking method or preparation style, dish positioning 
    - Do NOT invent ingredients that are not explicitly mentioned in the dish name
    - If a food term has a fixed, well-known translation, use the standard one
    - If unsure, use safe and general wording suitable for menus
    """

    user_prompt = f"""
    Target language: {target_language}

    Dish names:
    {dish_text}
    """

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "developer", "content": developer_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=300
    )

    lines = [line.strip() for line in response.choices[0].message.content.splitlines() if line.strip()]
    result = [{"name": name, "description": lines[i] if i < len(lines) else ""} for i, name in enumerate(dish_names)]
    return result