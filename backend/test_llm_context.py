import sys
import os
sys.path.append(os.getcwd())

from llm import llm_service
import json

print("Testing LLM Context & Group Chat Logic...")

# 模拟历史记录
chat_history = [
    {"sender": "System", "content": "欢迎入职！"},
    {"sender": "Me", "content": "大家好，我是新来的产品经理。"},
    {"sender": "Cai", "content": "欢迎，先把文档看了。"}
]

# 模拟群聊后续对话
context = {
    "player_action": "文档我看完了，关于那个Infra的需求我想讨论下。",
    "chat_history": chat_history,
    "game_state": {"role": "Product", "name": "Tester"},
    # 假设 Game.py 逻辑已经选择 Cai 作为 active_npc，或者我们在这里测试 LLM 如何处理指定 NPC
    "target_npc": {"name": "Cai", "role": "CTO", "traits": "技术宅神, 直率严厉"}
}

try:
    print("Sending request to LLM (Context Test)...")
    response = llm_service.generate_response(context)
    print("Response received:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
