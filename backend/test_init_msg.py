import requests

BASE_URL = "http://localhost:8000/api"

def test_init_msg():
    print("Initializing Game to check welcome message...")
    resp = requests.post(f"{BASE_URL}/init", json={"name": "Newbie", "role": "Dev", "project_name": "Genshin"})
    if resp.status_code != 200:
        print(f"Error: {resp.status_code}")
        return

    state = resp.json()
    history = state.get("chat_history", [])
    
    found_tutorial = False
    for msg in history:
        if msg["sender"] == "爱酱" and "生存指南" in msg["content"]:
            print("SUCCESS: Found tutorial message.")
            print("-" * 20)
            print(msg["content"])
            print("-" * 20)
            found_tutorial = True
            break
            
    if not found_tutorial:
        print("FAIL: Tutorial message not found.")
        print("Last messages:")
        for msg in history:
            print(f"{msg['sender']}: {msg['content']}")

if __name__ == "__main__":
    try:
        test_init_msg()
    except Exception as e:
        print(f"Error: {e}")
