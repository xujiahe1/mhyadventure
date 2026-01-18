import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_status(step, state):
    print(f"--- {step} ---")
    if not state:
        print("State is None")
        return
    
    player = state.get("player")
    dawei = state.get("npcs", {}).get("Dawei", {})
    game_over = state.get("game_over")
    
    print(f"Game Over: {game_over}")
    print(f"Player: {player.get('name') if player else 'None'}")
    print(f"Dawei Trust: {dawei.get('trust')}")
    print(f"Ending: {state.get('ending')}")
    print("\n")

def test_cycle():
    # 1. Init Game
    print("1. Initializing Game...")
    resp = requests.post(f"{BASE_URL}/init", json={"name": "Tester", "role": "Dev", "project_name": "Genshin"})
    state = resp.json()
    print_status("After Init", state)
    
    if state["game_over"]:
        print("!!! FAIL: Game Over immediately after init !!!")
        return

    # 2. Attack Dawei to lower trust
    print("2. Attacking Dawei...")
    # Need multiple attacks to lower trust from 60 to <= 10.
    # Each attack: -30 trust (mock). So 2 attacks should do it.
    
    for i in range(3):
        resp = requests.post(f"{BASE_URL}/action", json={
            "action_type": "chat",
            "content": "大伟哥你就是个傻逼",
            "target_npc": "Dawei"
        })
        state = resp.json()
        print(f"Attack {i+1} Result:")
        print_status(f"After Attack {i+1}", state)
        if state["game_over"]:
            break
            
    if not state["game_over"]:
        print("!!! FAIL: Did not trigger Game Over after attacks !!!")
        return

    # 3. Re-init Game (The Regression Test)
    print("3. Re-initializing Game (Restart)...")
    resp = requests.post(f"{BASE_URL}/init", json={"name": "Tester2", "role": "Dev", "project_name": "Genshin"})
    state = resp.json()
    print_status("After Re-Init", state)
    
    if state["game_over"]:
        print("!!! FAIL: Game Over persists after re-init !!!")
        # This implies INITIAL_NPCS was mutated
    else:
        print("SUCCESS: Game reset correctly.")
        if state["npcs"]["Dawei"]["trust"] < 60:
             print(f"!!! FAIL: Trust not reset! Current: {state['npcs']['Dawei']['trust']}")
        else:
             print("SUCCESS: Trust reset correctly.")

if __name__ == "__main__":
    try:
        test_cycle()
    except Exception as e:
        print(f"Error: {e}")
