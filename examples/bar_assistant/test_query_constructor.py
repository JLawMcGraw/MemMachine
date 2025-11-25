import os
import sys

# Ensure local imports work when running from repository root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_constructor import BarQueryConstructor


def test_constructs_flavor_spirit_intent():
    constructor = BarQueryConstructor()
    query = "Can you recommend a sweet whiskey drink?"

    result = constructor.create_query(query)

    assert 'User Query: "Can you recommend a sweet whiskey drink?"' in result
    assert "Intent: The user is asking for a recipe suggestion." in result
    assert "Primary Subject: The user is asking about whiskey." in result
    assert "Flavor Profile: The user mentioned a preference for sweet flavors." in result
    assert "CRITICAL CHECK" in result
    assert "CONVERSATION HISTORY" in result


def test_handles_allergy_statement_without_intent():
    constructor = BarQueryConstructor()
    query = "I'm allergic to peanuts."

    result = constructor.create_query(query)

    assert 'User Query: "I\'m allergic to peanuts."' in result
    assert "Intent: The user is asking for a recipe suggestion." not in result
    assert "CRITICAL CHECK" in result
