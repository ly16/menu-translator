from typing import Any, Dict
from google import genai
from google.genai import types

def get_dish_details(dish_name: str, target_language: str, restaurant: str, client: genai.Client) -> Dict[str, Any]:
    # 1. Parse the dish_context
    restaurant_name = f"at the restaurant '{restaurant}'" if restaurant else "in general or at popular locations"

    # 2. Configure Grounding (Google Search)
    # This is vital for finding specific restaurant reviews
    tools = [types.Tool(google_search=types.GoogleSearch())]
    prompt = f"""
        Search for reviews and food blogger mentions for the dish '{dish_name}' at the restaurant '{restaurant_name}'.
        
        In {target_language}, provide:
        1. A summary of customer sentiment (is it a signature dish?).
        2. Real-world feedback on the portion size and flavor.
        3. Provide any 'pro-tips' from reviewers, such as hidden ways to order the dish, custom modifications, or recommended food and drink pairings.".
        4. Provide the answer in a structured, easy-to-read format.
        5. provide a profile on a scale of 0-5:
            - Spiciness: (0=none, 5=fiery)
            - Sweetness: (0=savory, 5=dessert-like)
            - Acidity: (0=flat, 5=very tart)
            - Richness/Fat: (0=light/lean, 5=heavy/oily)
            - Texture: Describe if it's Crunchy, Tender, or Chewy.
        Note: If the specific restaurant is not provided or found, base the analysis on the most common authentic versions of this dish.
        """

    try:
        # 3. Use the Async (.aio) Gemini Client
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=tools,
                temperature=0.2
            )
        )

        sources = []
        metadata = response.candidates[0].grounding_metadata
        if metadata and metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web and chunk.web.uri:
                    sources.append(chunk.web.uri)
        return {
            "dish_name": dish_name,
            "details": response.text,
            "source_links": sources
        }

    except Exception as e:
        print(f"Error during calling Gemini: {e}")
        return []