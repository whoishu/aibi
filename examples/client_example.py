"""Example client usage of the autocomplete service"""

import json

import requests


class AutocompleteClient:
    """Simple client for autocomplete service"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client

        Args:
            base_url: Base URL of the autocomplete service
        """
        self.base_url = base_url.rstrip("/")
        self.api_prefix = "/api/v1"

    def get_suggestions(self, query: str, user_id: str = None, limit: int = 10):
        """Get autocomplete suggestions

        Args:
            query: User input query
            user_id: Optional user ID for personalization
            limit: Maximum number of suggestions

        Returns:
            List of suggestions
        """
        url = f"{self.base_url}{self.api_prefix}/autocomplete"

        payload = {"query": query, "limit": limit}

        if user_id:
            payload["user_id"] = user_id

        response = requests.post(url, json=payload)
        response.raise_for_status()

        return response.json()

    def submit_feedback(self, query: str, selected: str, user_id: str = None):
        """Submit user feedback

        Args:
            query: Original query
            selected: Selected suggestion
            user_id: Optional user ID

        Returns:
            Response data
        """
        url = f"{self.base_url}{self.api_prefix}/feedback"

        payload = {"query": query, "selected_suggestion": selected}

        if user_id:
            payload["user_id"] = user_id

        response = requests.post(url, json=payload)
        response.raise_for_status()

        return response.json()

    def add_document(self, text: str, keywords: list = None, metadata: dict = None):
        """Add a document to the index

        Args:
            text: Document text
            keywords: Optional list of keywords
            metadata: Optional metadata

        Returns:
            Response data
        """
        url = f"{self.base_url}{self.api_prefix}/documents"

        payload = {"text": text}

        if keywords:
            payload["keywords"] = keywords
        if metadata:
            payload["metadata"] = metadata

        response = requests.post(url, json=payload)
        response.raise_for_status()

        return response.json()

    def health_check(self):
        """Check service health

        Returns:
            Health status data
        """
        url = f"{self.base_url}{self.api_prefix}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def example_usage():
    """Example usage of the autocomplete client"""

    # Initialize client
    client = AutocompleteClient()

    print("=== Example 1: Get Suggestions ===")
    result = client.get_suggestions("销售", user_id="user123")
    print(f"Query: {result['query']}")
    print(f"Found {result['total']} suggestions:")
    for suggestion in result["suggestions"]:
        print(f"  - {suggestion['text']} (score: {suggestion['score']})")

    print("\n=== Example 2: Submit Feedback ===")
    if result["suggestions"]:
        selected = result["suggestions"][0]["text"]
        feedback_result = client.submit_feedback("销售", selected, user_id="user123")
        print(f"Feedback result: {feedback_result}")

    print("\n=== Example 3: Get Personalized Suggestions ===")
    # After feedback, the same query should be influenced by user preference
    result2 = client.get_suggestions("销售", user_id="user123")
    print(f"Found {result2['total']} suggestions (with personalization):")
    for suggestion in result2["suggestions"]:
        print(
            f"  - {suggestion['text']} (score: {suggestion['score']}, source: {suggestion['source']})"
        )

    print("\n=== Example 4: Add Custom Document ===")
    add_result = client.add_document(
        text="季度业绩报告",
        keywords=["quarterly", "performance", "report", "季度", "业绩"],
        metadata={"type": "report", "category": "performance"},
    )
    print(f"Add document result: {add_result}")

    print("\n=== Example 5: Health Check ===")
    health = client.health_check()
    print(f"Service health: {json.dumps(health, indent=2)}")


if __name__ == "__main__":
    try:
        example_usage()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to service. Is it running?")
    except Exception as e:
        print(f"Error: {e}")
