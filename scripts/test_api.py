"""Simple test script for the autocomplete API"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_autocomplete(query, user_id=None):
    """Test autocomplete endpoint"""
    print(f"\n=== Testing Autocomplete: '{query}' ===")
    
    payload = {
        "query": query,
        "limit": 5
    }
    
    if user_id:
        payload["user_id"] = user_id
    
    response = requests.post(
        f"{BASE_URL}/api/v1/autocomplete",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Query: {data['query']}")
        print(f"Total Suggestions: {data['total']}")
        print("\nSuggestions:")
        for i, suggestion in enumerate(data['suggestions'], 1):
            print(f"  {i}. {suggestion['text']}")
            print(f"     Score: {suggestion['score']}, Source: {suggestion['source']}")
    else:
        print(f"Error: {response.text}")
    
    return response.json() if response.status_code == 200 else None


def test_feedback(query, selected, user_id="test_user"):
    """Test feedback endpoint"""
    print(f"\n=== Testing Feedback ===")
    
    payload = {
        "query": query,
        "selected_suggestion": selected,
        "user_id": user_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/feedback",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_add_document():
    """Test adding a document"""
    print("\n=== Testing Add Document ===")
    
    payload = {
        "text": "测试自动补全功能",
        "keywords": ["test", "autocomplete", "测试"],
        "metadata": {"category": "test"}
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/documents",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("=" * 60)
    print("ChatBI Autocomplete Service - Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Is the service running?")
        return
    
    print("\n✓ Service is healthy")
    
    # Wait a bit for service to be ready
    time.sleep(1)
    
    # Test 2: Chinese query
    result = test_autocomplete("销售")
    
    # Test 3: English query
    test_autocomplete("sales")
    
    # Test 4: Mixed query
    test_autocomplete("销售trend")
    
    # Test 5: Partial match
    test_autocomplete("用户")
    
    # Test 6: Feedback (if we got results)
    if result and result['suggestions']:
        first_suggestion = result['suggestions'][0]['text']
        test_feedback("销售", first_suggestion, "test_user_001")
    
    # Test 7: Personalized query (same query as before)
    print("\n--- Testing Personalization (should boost previous selection) ---")
    test_autocomplete("销售", user_id="test_user_001")
    
    # Test 8: Add document
    test_add_document()
    
    # Wait for indexing
    time.sleep(1)
    
    # Test 9: Query for newly added document
    test_autocomplete("测试")
    
    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to service at", BASE_URL)
        print("Please ensure the service is running:")
        print("  python app/main.py")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
