import requests
import json

def test_chat_action():
    url = "http://localhost:8000/chat"
    
    # 1. Check initial stats
    stats_url = "http://localhost:8000/stats"
    try:
        initial_stats = requests.get(stats_url).json()
        print(f"Initial Stats: {initial_stats}")
        
        # 2. Send a message that should trigger an action (hunger decrease)
        payload = {"message": "Here is a big delicious apple for you, Byte!"}
        print(f"Sending message: {payload['message']}")
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Pet Reply: {data['reply']}")
        print(f"Updated Stats: {data['stats']}")
        
        if data['stats']['hunger'] < initial_stats['hunger']:
            print("SUCCESS: Hunger decreased!")
        else:
            print("FAILURE: Hunger did not decrease. (Note: LLM might not have generated the action)")
            
    except Exception as e:
        print(f"Test failed: {e}. Is the backend running?")

if __name__ == "__main__":
    test_chat_action()
