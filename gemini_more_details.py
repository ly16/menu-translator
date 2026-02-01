from typing import Any, Dict, List
from google import genai
from google.genai import types
from config import GEMINI_BATCH_SIZE
import asyncio

async def get_dish_details(dish_list: List[str], target_language: str, restaurant: str, client: genai.Client) -> Dict[str, Any]:
    # 1. Parse the dish_context
    restaurant_name = f"at the restaurant '{restaurant}'" if restaurant else "in general or at popular locations"

    # 2. Call Gemini in parallel
    batches = [dish_list[i:i + GEMINI_BATCH_SIZE] for i in range(0, len(dish_list), GEMINI_BATCH_SIZE)]
    # Create a list of tasks for concurrent execution
    tasks = [
        process_batch(batch, target_language, restaurant_name, client)
        for batch in batches
    ]
    # Run all batches in parallel
    results_nested = await asyncio.gather(*tasks)
    # Flatten the list of lists into a single list
    return [item for sublist in results_nested for item in sublist]

async def process_batch(dish_list: List[str], target_language: str, restaurant_name: str, client: genai.Client) -> List[
    Dict[str, Any]]:
    tools = [types.Tool(google_search=types.GoogleSearch())]

    prompt = f"""
        Act as a professional food critic. Search for recent reviews and food blogger
        Iterate through the LIST OF DISHES {dish_list} at the restaurant {restaurant_name},
        and create a separate block for EACH item.
        Keep the field keys dish_name exactly as written below to act as parsing anchors.

        OUTPUT RULES:
        1. Provide ONLY raw plain text. No Markdown.
        2. Field keys must stay in English (dish_name, details) to serve as parsing anchors.
        3. The "details" field must be a single, cohesive paragraph containing: 
           - Sentiment (Signature/Hidden Gem)
           - Feedback (Portion/Flavor)
           - Pro-tips (Hacks/Pairings)
           - Numerical ratings (Spiciness, Sweetness, Acidity, Richness on a 0-5 scale)
           - Texture keywords

        STRUCTURE PER DISH:
        === DISH_START ===
        dish_name: [Original Name from dish_list]
        details: [Write all descriptive content here in {target_language}]
        === DISH_END ===

        Note: If the specific restaurant is not found, base analysis on the most 
        common authentic versions. Do not include introductory text; start directly 
        with the first DISH_START marker.
        """

    try:
        # Use the Async (.aio) Gemini Client
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=tools,
                temperature=0.2
            )
        )
        parsed_items = parse_dish_report(response.text)
        valid_link = ""
        valid_title = ""
        if response.candidates[0].grounding_metadata and response.candidates[0].grounding_metadata.grounding_chunks:
            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                if chunk.web and chunk.web.uri:
                    valid_link = chunk.web.uri
                    valid_title = chunk.web.title
                    break  # Just take the top 1 source
        for item in parsed_items:
            item["link"] = valid_link
            item["link_title"] = valid_title
        return parsed_items
    except Exception as e:
        print(f"Error during calling Gemini {dish_list}: {e}")
        return []

def parse_dish_report(raw_text):
    blocks = raw_text.split("=== DISH_START ===")
    results = []

    for block in blocks:
        if "=== DISH_END ===" not in block:
            continue

        content = block.split("=== DISH_END ===")[0].strip()
        lines = content.split('\n')

        # Initialize dictionary
        entry = {"dish_name": "", "details": "", "link": "", "link_title": ""}

        for line in lines:
            line = line.strip()
            if not line: continue

            # Simple keyword matching for anchors
            if line.lower().startswith("dish_name:"):
                entry["dish_name"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("details:"):
                entry["details"] = line.split(":", 1)[1].strip()
            else:
                # If a field overflows to a second line, append it to details
                if entry["details"]:
                    entry["details"] += " " + line

        results.append(entry)
    return results