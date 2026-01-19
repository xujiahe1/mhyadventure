import requests
import json
import time

BASE_URL = "http://localhost:8000/api"


def measure_init(times: int = 3):
    url = f"{BASE_URL}/init"
    payload = {
        "name": "TestPlayer",
        "role": "Dev",
        "project_name": "Genshin",
    }
    costs = []
    for i in range(times):
        try:
            print(f"[INIT] Round {i + 1} POST {url}")
            t0 = time.perf_counter()
            res = requests.post(url, json=payload, timeout=60)
            t1 = time.perf_counter()
            cost = t1 - t0
            costs.append(cost)
            print(f"[INIT] Status {res.status_code}, cost {cost:.3f}s")
            if res.status_code == 200 and i == 0:
                resp_json = res.json()
                print("[INIT] Year:", resp_json.get("year"))
                print("[INIT] Quarter:", resp_json.get("quarter"))
                print("[INIT] Week:", resp_json.get("week"))
        except Exception as e:
            print(f"[INIT] Failed: {e}")
    if costs:
        avg = sum(costs) / len(costs)
        print(f"[INIT] Avg cost over {len(costs)} rounds: {avg:.3f}s")


def measure_action(times: int = 3):
    url = f"{BASE_URL}/action"
    payload = {
        "action_type": "chat",
        "content": "大家好，今天的工作怎么安排？",
        "target_npc": "group",
    }
    costs = []
    for i in range(times):
        try:
            print(f"[ACTION] Round {i + 1} POST {url}")
            t0 = time.perf_counter()
            res = requests.post(url, json=payload, timeout=60)
            t1 = time.perf_counter()
            cost = t1 - t0
            costs.append(cost)
            print(f"[ACTION] Status {res.status_code}, cost {cost:.3f}s")
        except Exception as e:
            print(f"[ACTION] Failed: {e}")
    if costs:
        avg = sum(costs) / len(costs)
        print(f"[ACTION] Avg cost over {len(costs)} rounds: {avg:.3f}s")


def measure_action_stream(times: int = 3):
    url = f"{BASE_URL}/action/stream"
    payload = {
        "action_type": "chat",
        "content": "大家好，最近项目风险怎么样？",
        "target_npc": None,
    }
    first_token_costs = []
    full_costs = []
    for i in range(times):
        try:
            print(f"[STREAM] Round {i + 1} POST {url}")
            t0 = time.perf_counter()
            res = requests.post(url, json=payload, timeout=60, stream=True)
            first_token_time = None
            for line in res.iter_lines(decode_unicode=True):
                if not line:
                    continue
                now = time.perf_counter()
                if first_token_time is None:
                    first_token_time = now
                last_time = now
            t_end = last_time if first_token_time is not None else time.perf_counter()
            if first_token_time is not None:
                first_cost = first_token_time - t0
                full_cost = t_end - t0
                first_token_costs.append(first_cost)
                full_costs.append(full_cost)
                print(f"[STREAM] Status {res.status_code}, first token {first_cost:.3f}s, full {full_cost:.3f}s")
            else:
                print("[STREAM] No data received")
        except Exception as e:
            print(f"[STREAM] Failed: {e}")
    if first_token_costs:
        avg_first = sum(first_token_costs) / len(first_token_costs)
        avg_full = sum(full_costs) / len(full_costs)
        print(f"[STREAM] Avg first token over {len(first_token_costs)} rounds: {avg_first:.3f}s")
        print(f"[STREAM] Avg full stream over {len(full_costs)} rounds: {avg_full:.3f}s")


if __name__ == "__main__":
    print("=== Measure /api/init ===")
    measure_init()
    print("\n=== Measure /api/action ===")
    measure_action()
    print("\n=== Measure /api/action/stream ===")
    measure_action_stream()
