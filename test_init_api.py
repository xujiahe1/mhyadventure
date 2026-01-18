import requests
import json

url = "http://localhost:8000/api/init"
data = {
    "name": "TestPlayer",
    "role": "Dev",
    "project_name": "Genshin"
}

try:
    print(f"Sending POST to {url}...")
    res = requests.post(url, json=data, timeout=60)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        resp_json = res.json()
        print("Response keys:", resp_json.keys())
        print("Year:", resp_json.get("year"))
        print("Quarter:", resp_json.get("quarter"))
        print("Week:", resp_json.get("week"))
        print("Player:", resp_json.get("player"))
    else:
        print("Error:", res.text)
except Exception as e:
    print(f"Request failed: {e}")
