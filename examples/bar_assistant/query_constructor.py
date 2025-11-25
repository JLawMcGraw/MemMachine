# File: memmachine/examples/bar_assistant/query_constructor.py

import sys
import os
from typing import Dict, Any

# Ensure we can import from the parent 'examples' directory to access MemMachine's base classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_query_constructor import BaseQueryConstructor


class BarQueryConstructor(BaseQueryConstructor):
    """
    Constructs a specialized search query for the Alchemix memory store.

    This class enhances the user's raw query with semantic keywords and explicit
    instructions for the retrieval system, focusing on flavor profiles, spirit types,
    and crucial user constraints like allergies or dislikes.
    """

    def create_query(self, query: str, **kwargs) -> str:
        """
        Transforms a simple user input string into a rich, semantic search query.

        Args:
            query: The raw chat message from the user (e.g., "I want something fruity").
            **kwargs: Additional context if needed (e.g., user_id).

        Returns:
            A detailed string that will be converted into a vector embedding for searching memories.
        """
        # 1. Define High-Value Keywords for Semantic Enrichment
        # These lists can be expanded over time.
        flavors = [
            "sweet",
            "sour",
            "bitter",
            "smoky",
            "dry",
            "fruity",
            "spicy",
            "herbal",
            "creamy",
            "tart",
            "refreshing",
            "citrus",
            "tropical",
            "floral",
            "earthy",
        ]
        spirits = [
            "gin",
            "vodka",
            "rum",
            "whiskey",
            "bourbon",
            "scotch",
            "tequila",
            "mezcal",
            "brandy",
            "cognac",
            "liqueur",
            "vermouth",
        ]
        actions = ["make", "suggest", "recommend", "create", "find", "want", "need"]

        lower_query = query.lower()
        found_flavors = [f for f in flavors if f in lower_query]
        found_spirits = [s for s in spirits if s in lower_query]
        is_suggestion_request = any(action in lower_query for action in actions)

        # 2. Construct a Rich Search Context
        # This detailed prompt guides the vector search to find the most relevant memories.
        # It's more effective than just using the raw query.
        search_context = f'User Query: "{query}"\n'

        if is_suggestion_request:
            search_context += (
                "Intent: The user is asking for a recipe suggestion.\n"
            )

        if found_spirits:
            search_context += f"Primary Subject: The user is asking about {', '.join(found_spirits)}. Search for recipes containing these spirits and any past user feedback related to them.\n"

        if found_flavors:
            search_context += f"Flavor Profile: The user mentioned a preference for {', '.join(found_flavors)} flavors. Prioritize memories matching this taste profile.\n"

        # 3. Add Mandatory Checks for Critical User-Specific Constraints
        # This ensures that safety and strong preferences are always checked.
        search_context += "CRITICAL CHECK: Always retrieve memories related to user's stated 'dislikes', 'hates', 'allergies', or 'never wants' to ensure suggestions are safe and enjoyable.\n"

        # 4. Add instruction to retrieve past conversations
        search_context += "CONVERSATION HISTORY: Retrieve any past conversations or interactions with the user that might provide context for this query.\n"

        print(f"Constructed Query for Embedding:\n---\n{search_context}\n---")

        return search_context
