#!/usr/bin/env python3
"""
Test the deployed Calendar AI API
"""

import requests
import json

# API Configuration
API_BASE_URL = "https://eabzln975h.execute-api.us-east-1.amazonaws.com/prod"
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"

def test_api_endpoints():
    """Test all API endpoints"""
    
    print("🧪 Testing Nextcloud Calendar AI API")
    print("=" * 50)
    
    # Test 1: API Info
    print("\n1. Testing API Info...")
    try:
        response = requests.get(API_BASE_URL)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: List Events
    print("\n2. Testing List Events...")
    try:
        response = requests.get(f"{API_BASE_URL}/events")
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"📅 Found {data.get('total', 0)} events")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Find Slots
    print("\n3. Testing Find Slots...")
    try:
        response = requests.get(f"{API_BASE_URL}/slots", params={
            'duration': '60',
            'date': 'tomorrow',
            'preferences': 'morning'
        })
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"🔍 Found {len(data.get('available_slots', []))} available slots")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: AI Chat
    print("\n4. Testing AI Chat...")
    test_messages = [
        "Hello! What can you help me with?",
        "What's on my calendar today?",
        "Find me a 1-hour slot tomorrow morning"
    ]
    
    for message in test_messages:
        try:
            print(f"\n💬 User: {message}")
            response = requests.post(CHAT_ENDPOINT, json={'message': message})
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 AI: {data.get('message', 'No response')}")
            else:
                print(f"❌ Error response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")

def test_create_event():
    """Test creating a new event"""
    
    print("\n📝 Testing Event Creation...")
    
    event_data = {
        "title": "Test Meeting",
        "start_time": "2024-01-16T14:00:00Z",
        "duration": 60,
        "description": "API test event"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/events", json=event_data)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    test_create_event()