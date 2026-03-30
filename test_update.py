import requests
import json
import time

API_URL = "http://localhost:8000/api/v1"

def test_modification():
    print("Testing Modification Query...")
    payload = {
        "user_query": "Chris Anderson change his review as 3",
        "top_k": 3
    }

    start = time.time()
    resp = requests.post(f"{API_URL}/query", json=payload)
    end = time.time()

    print(f"Status Code: {resp.status_code}")
    print(f"Time Taken: {end - start:.2f}s")
    
    try:
        data = resp.json()
        print("\nResponse:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Failed to parse JSON:", str(e))
        print("Raw text:", resp.text)

if __name__ == "__main__":
    test_modification()
