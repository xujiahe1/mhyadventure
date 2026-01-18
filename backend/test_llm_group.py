import sys
import os
sys.path.append(os.getcwd())

from llm import llm_service
import json

print("Testing LLM Group Chat...")

# 模拟群聊，无特定目标
context = {
    "player_action": "大家早上好啊，今天有什么安排？",
    "game_state": {"role": "Dev", "name": "Tester"},
    "target_npc": None
}

try:
    print("Sending request to LLM (Group Chat)...")
    response = llm_service.generate_response(context)
    print("Response received:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
