import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "npcs.json")
PRESERVE_KEYS = set()

COMMON_SURNAMES = set(list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳唐罗薛尤任杜阮闵席季顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧戴宋茅庞熊纪舒屈项祝董粱杜阮蓝采"))
GIVEN_POOL = ["衡","砚","屿","澜","宁","曜","晏","行","临","槿","潇","然","祁","珺","宸","沐","岑","澈","瑜","墨","澜","岚","晗","玥","凝","珩","砺","砾","衡","砚","潞","珞","菡","芷","笙","尧","尘","喆","翊","祎","琪","苏","槐","渝","景","澈","恺","澄","渊","湛","沁","泽","言"]

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

def _is_cjk(s: str) -> bool:
    return any('\u4e00' <= ch <= '\u9fff' for ch in s or "")

def _dedupe_name(original: str, npc_id: str, used_names: set) -> str:
    name = (original or "").strip()
    base = name
    if _is_cjk(name) and len(name) >= 2:
        surname = name[0] if name[0] in COMMON_SURNAMES else name[0]
        idx = sum(ord(c) for c in npc_id) % len(GIVEN_POOL)
        given = GIVEN_POOL[idx]
        candidate = surname + given
        tries = 0
        while candidate in used_names and tries < 5:
            idx = (idx + 7) % len(GIVEN_POOL)
            candidate = surname + GIVEN_POOL[idx]
            tries += 1
        return candidate
    else:
        idx = sum(ord(c) for c in npc_id) % len(GIVEN_POOL)
        candidate = name + GIVEN_POOL[idx]
        tries = 0
        while candidate in used_names and tries < 5:
            idx = (idx + 5) % len(GIVEN_POOL)
            candidate = name + GIVEN_POOL[idx]
            tries += 1
        return candidate

def ensure_unique_names(npcs, mapping):
    name_to_ids = {}
    for old_key, data in npcs.items():
        name = str(data.get("name", "")).strip()
        name_to_ids.setdefault(name, []).append(old_key)
    used_names = set()
    for data in npcs.values():
        nm = str(data.get("name", "")).strip()
        if nm:
            used_names.add(nm)
    for name, ids in name_to_ids.items():
        if len(ids) <= 1:
            continue
        for idx, old_key in enumerate(ids):
            new_key = mapping.get(old_key, old_key)
            data = npcs[old_key]
            if idx == 0:
                used_names.add(name)
                data["name"] = name
            else:
                new_name = _dedupe_name(name, new_key, used_names)
                used_names.add(new_name)
                data["name"] = new_name
    return npcs

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

    new_npcs = {}
    for old_key, data in npcs.items():
        new_key = mapping[old_key]
        data["id"] = new_key
        m = data.get("manager_id")
        if isinstance(m, str):
            data["manager_id"] = mapping.get(m, m)
        data["relations"] = remap_relations(data.get("relations", {}), mapping)
        name = str(data.get("name", "")).strip()
        if "（" in name and "）" in name:
            base = name.split("（")[0].strip()
            data["name"] = base
        elif "(" in name and ")" in name:
            base = name.split("(")[0].strip()
            data["name"] = base

        new_npcs[new_key] = data

    new_npcs = ensure_unique_names(new_npcs, mapping)

    save_json(DATA_PATH, new_npcs)
    print(f"Remapped {len(npcs)} NPC entries. All IDs normalized to NPC_ format and names de-duplicated.")

if __name__ == "__main__":
    main()
