import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "npcs.json")

# IDs that must be preserved to avoid breaking game logic
PRESERVE_KEYS = {"Cai", "Dawei", "Luo"}

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def collect_existing_numbers(npcs):
    nums = set()
    for key in npcs.keys():
        if key.startswith("NPC_"):
            suffix = key.replace("NPC_", "")
            if suffix.isdigit():
                nums.add(int(suffix))
    return nums

def next_npc_id(existing_nums):
    n = max(existing_nums) + 1 if existing_nums else 1001
    while n in existing_nums:
        n += 1
    existing_nums.add(n)
    return f"NPC_{n:04d}"

def build_id_mapping(npcs):
    existing_nums = collect_existing_numbers(npcs)
    mapping = {}
    for old_key in list(npcs.keys()):
        if old_key in PRESERVE_KEYS:
            mapping[old_key] = old_key
            continue
        if old_key.startswith("NPC_"):
            mapping[old_key] = old_key
            # ensure data.id will be aligned later
            continue
        # assign new NPC_ id
        new_key = next_npc_id(existing_nums)
        mapping[old_key] = new_key
    return mapping

def remap_relations(relations, mapping):
    if not isinstance(relations, dict):
        return relations
    new_rel = {}
    for k, v in relations.items():
        new_k = mapping.get(k, k)
        new_rel[new_k] = v
    return new_rel

def main():
    npcs = load_json(DATA_PATH)
    mapping = build_id_mapping(npcs)

    # Construct new npc dict with remapped keys and updated fields
    new_npcs = {}
    for old_key, data in npcs.items():
        new_key = mapping[old_key]
        # Update id field
        data["id"] = new_key
        # Update manager_id
        m = data.get("manager_id")
        if isinstance(m, str):
            data["manager_id"] = mapping.get(m, m)
        # Update relations map keys
        data["relations"] = remap_relations(data.get("relations", {}), mapping)
        # Normalize name suffixes just in case
        name = str(data.get("name", "")).strip()
        if "（" in name and "）" in name:
            # remove Chinese parentheses content
            base = name.split("（")[0].strip()
            data["name"] = base
        elif "(" in name and ")" in name:
            base = name.split("(")[0].strip()
            data["name"] = base

        new_npcs[new_key] = data

    save_json(DATA_PATH, new_npcs)
    print(f"Remapped {len(npcs)} NPC entries. Preserved keys: {', '.join(sorted(PRESERVE_KEYS))}")

if __name__ == "__main__":
    main()

