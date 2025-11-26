"""
Quick test of all new endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    resp = requests.get(f"{BASE_URL}/health")
    print(f"✓ Health: {resp.json()}")

def test_stats():
    """Test stats endpoint"""
    resp = requests.get(f"{BASE_URL}/stats")
    print(f"✓ Stats: {resp.json()}")

def test_legal_stats():
    """Test legal database stats"""
    resp = requests.get(f"{BASE_URL}/api/legal/stats")
    print(f"✓ Legal Stats: {resp.json()}")

def test_legal_search():
    """Test legal article search"""
    resp = requests.get(f"{BASE_URL}/api/legal/search", params={"q": "договор", "limit": 3})
    result = resp.json()
    print(f"✓ Legal Search: Found {result['count']} articles")
    if result['results']:
        print(f"  First result: {result['results'][0]['article_number']} - {result['results'][0]['content'][:100]}...")

if __name__ == "__main__":
    print("🧪 Testing Credit Guardian API Endpoints\n")
    
    try:
        test_health()
        test_stats()
        test_legal_stats()
        test_legal_search()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
