from llm import llm_service
import json

print("Testing LLM Connection...")
print(f"Using Mock: {llm_service.use_mock}")

context = {
    "player_action": "你好，蔡总",
    "game_state": {"role": "Dev", "name": "Tester"},
    "target_npc": {"name": "Cai", "role": "CTO", "traits": "技术宅神"}
}

try:
    print("Sending request to LLM...")
    response = llm_service.generate_response(context)
    print("Response received:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
