# File: memmachine/examples/bar_assistant/ingest_recipes.py

import requests
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
# The URL for MemMachine's memory creation endpoint.
MEMMACHINE_API_URL = os.getenv("MEMMACHINE_API_URL", "http://localhost:8001/memory")

# The URL for the Alchemix API's recipe endpoint.
# Assumes the backend is running and accessible during ingestion.
ALCHEMIX_API_URL = os.getenv("ALCHEMIX_API_URL", "http://localhost:3000/api/recipes")

# A special, system-level user ID to hold global, non-user-specific knowledge.
# This ensures recipes are retrieved for ALL users.
KNOWLEDGE_BASE_USER_ID = "system_knowledge_base" 

# A valid JWT token from Alchemix is required to access the /api/recipes endpoint.
# This should be acquired by logging in with a test user.
ALCHEMIX_JWT_TOKEN = os.getenv("ALCHEMIX_JWT_TOKEN", "")


def fetch_recipes_from_alchemix():
    """Fetches all recipes from the Alchemix API with pagination."""
    logger.info(f"Fetching recipes from {ALCHEMIX_API_URL}...")
    headers = {
        "Authorization": f"Bearer {ALCHEMIX_JWT_TOKEN}"
    }
    all_recipes = []
    page = 1
    limit = 100  # API max limit per page

    try:
        while True:
            response = requests.get(ALCHEMIX_API_URL, headers=headers, params={"limit": limit, "page": page})
            response.raise_for_status()
            data = response.json()

            # Handle paginated response format
            if isinstance(data, dict) and 'data' in data:
                recipes = data['data']
                pagination = data.get('pagination', {})
                all_recipes.extend(recipes)

                logger.info(f"Fetched page {page}: {len(recipes)} recipes (total so far: {len(all_recipes)})")

                # Check if there are more pages
                if not pagination.get('hasNextPage', False):
                    break
                page += 1
            else:
                # Fallback for non-paginated response
                all_recipes = data.get('recipes', data) if isinstance(data, dict) else data
                break

        logger.info(f"Successfully fetched {len(all_recipes)} recipes total.")
        return all_recipes
    except Exception as e:
        logger.error(f"❌ CRITICAL: Failed to fetch recipes from Alchemix API. Error: {e}")
        logger.error("Please ensure the Alchemix backend is running and the JWT token is valid.")
        return []


def ingest_recipe(recipe: dict):
    """Ingests a single recipe into MemMachine."""
    
    # Parse ingredients - handle both string and array formats
    ingredients = recipe.get('ingredients', [])
    if isinstance(ingredients, str):
        try:
            ingredients = json.loads(ingredients)
        except:
            ingredients = [ingredients]
    
    ingredients_text = ', '.join(ingredients) if isinstance(ingredients, list) else str(ingredients)
    
    # Create a text representation of the recipe for semantic search.
    # The more descriptive this is, the better the search results.
    recipe_text = (
        f"Recipe for {recipe.get('name', 'N/A')}. "
        f"Category: {recipe.get('category', 'Classic Cocktail')}. "
        f"Glass: {recipe.get('glass', 'N/A')}. "
        f"Ingredients: {ingredients_text}. "
        f"Instructions: {recipe.get('instructions', 'N/A')}"
    )
    
    logger.info(f"Ingesting: {recipe.get('name')}")
    
    try:
        # Use the /memory POST endpoint format from example_server.py
        response = requests.post(
            MEMMACHINE_API_URL,
            params={
                "user_id": KNOWLEDGE_BASE_USER_ID,
                "query": recipe_text
            },
            timeout=30
        )
        response.raise_for_status()
        logger.info(f"✅ Ingested Recipe: {recipe.get('name')}")
    except Exception as e:
        logger.error(f"❌ Failed to ingest {recipe.get('name')}. Error: {e}")


if __name__ == "__main__":
    if not ALCHEMIX_JWT_TOKEN:
        logger.warning("⚠️  WARNING: ALCHEMIX_JWT_TOKEN is not set.")
        logger.warning("Please set it as an environment variable:")
        logger.warning("  export ALCHEMIX_JWT_TOKEN='your_token_here'")
        logger.warning("\nTo get a token:")
        logger.warning("  1. Start Alchemix backend (npm run dev:api)")
        logger.warning("  2. Login to the UI")
        logger.warning("  3. Open browser DevTools > Application > Local Storage")
        logger.warning("  4. Copy the 'token' value")
        exit(1)
    else:
        logger.info("🚀 Starting Alchemix Recipe Ingestion for MemMachine...")
        recipes = fetch_recipes_from_alchemix()
        if recipes:
            logger.info(f"\nIngesting {len(recipes)} recipes into knowledge base...")
            for r in recipes:
                ingest_recipe(r)
            logger.info("\n✅ Ingestion process complete.")
        else:
            logger.error("No recipes found to ingest.")
