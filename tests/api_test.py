import requests
import json

def test_api():
    # Base URL - using the exposed port from the container
    base_url = "http://localhost:8000"
    
    print("1. Testing health endpoint...")
    try:
        health_response = requests.get(f"{base_url}/health")
        print(f"Health check status: {health_response.status_code}")
        print(f"Response: {health_response.json()}\n")
    except Exception as e:
        print(f"Health check failed: {str(e)}\n")

    print("2. Testing chat endpoint...")
    try:
        chat_data = {
            "message": "Tôi bị đau đầu và sốt",
            "patient_id": "TEST001"
        }
        chat_response = requests.post(f"{base_url}/chat", json=chat_data)
        print(f"Chat status: {chat_response.status_code}")
        print(f"Response: {chat_response.json()}\n")
    except Exception as e:
        print(f"Chat test failed: {str(e)}\n")

    print("3. Testing queue status endpoint...")
    try:
        queue_data = {
            "specialty": "Nội khoa"
        }
        queue_response = requests.post(f"{base_url}/queue-status", json=queue_data)
        print(f"Queue status: {queue_response.status_code}")
        print(f"Response: {queue_response.json()}\n")
    except Exception as e:
        print(f"Queue status test failed: {str(e)}\n")

if __name__ == "__main__":
    test_api()
