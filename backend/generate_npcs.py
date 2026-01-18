import asyncio
import json
import os
import random
from openai import AsyncOpenAI
from faker import Faker

# Configuration
API_BASE = "https://llm-open-ai-private.mihoyo.com/v1"
API_KEY = "56da33c3-2075-4741-8bcc-378f879d49cf"
MODEL = "mihoyo-deepseek-v3.2-chat"
OUTPUT_FILE = "backend/data/npcs.json"
TARGET_COUNT = 1000

fake = Faker("zh_CN")

client = AsyncOpenAI(base_url=API_BASE, api_key=API_KEY, timeout=10.0)

async def generate_npc_templates(count=20):
    print(f"Generating {count} NPC templates via LLM...")
    prompt = f"""
    Generate {count} unique NPC templates for a tech company RPG (MiHoYo style).
    JSON Format list of objects:
    [
      {{
        "role": "Position (例如 研发, 产品, 运营, 美术)",
        "traits": "Personality traits (e.g. 卷王, 摸鱼怪, 技术大牛)",
        "project": "Project Name (Honkai3, Genshin, HSR, ZZZ, HYG, IAM, General)"
      }}
    ]
    Make them diverse and funny. Output JSON only.
    """
    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        # Ensure it's a list under a key or direct list
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif "npcs" in data:
            return data["npcs"]
        else:
            # Fallback if structure is weird
            return list(data.values())[0]
            
    except Exception as e:
        print(f"LLM Error: {e}")
        # Fallback templates
        return [
            {"role": "Dev", "traits": "秃顶强者", "project": "Genshin"},
            {"role": "Product", "traits": "需求制造机", "project": "HSR"},
            {"role": "Art", "traits": "唯美主义", "project": "ZZZ"},
            {"role": "Ops", "traits": "背锅侠", "project": "IAM"}
        ]

def generate_npcs(templates):
    npcs = {}
    projects = ["Honkai3", "Genshin", "HSR", "ZZZ", "HYG", "IAM", "General", "HR", "Marketing"]
    
    # 1. Keep Existing Important NPCs (Hardcoded in game.py originally)
    # We will merge them later in game.py or here. 
    # Let's generate new ones to append.
    
    print(f"Generating {TARGET_COUNT} NPCs based on templates...")
    
    for i in range(TARGET_COUNT):
        template = random.choice(templates)

        npc_id = f"NPC_{i+1:04d}"

        name = fake.name()

        role = template["role"]
        traits = template["traits"]
        project = template.get("project", random.choice(projects))

        trust = random.randint(30, 70)
        mood = random.randint(50, 90)
        level = random.choice(["P4", "P5", "P6", "P7"])
        status = "在职"

        npcs[npc_id] = {
            "id": npc_id,
            "name": f"{name} ({role})",
            "role": role,
            "traits": traits,
            "project": project,
            "trust": trust,
            "mood": mood,
            "level": level,
            "status": status
        }
        
    return npcs

async def main():
    # 1. Get Templates from LLM
    templates = await generate_npc_templates(20)
    print(f"Got {len(templates)} templates.")
    
    # 2. Generate Bulk
    npcs = generate_npcs(templates)
    
    # 3. Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(npcs, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved {len(npcs)} NPCs to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
