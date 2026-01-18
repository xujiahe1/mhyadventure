from models import NPC
from pydantic import BaseModel

# Mock NPC if import fails (but it should work)
# class NPC(BaseModel):
#     id: str
#     name: str
#     trust: int = 50

cai = NPC(id="Cai", name="Cai", trust=50)
initial_npcs = {"Cai": cai}

# Simulation of init_game
state_npcs = {k: v.copy() for k, v in initial_npcs.items()}

# Modify state
state_npcs["Cai"].trust = 0

print(f"State Trust: {state_npcs['Cai'].trust}")
print(f"Initial Trust: {initial_npcs['Cai'].trust}")

if initial_npcs["Cai"].trust == 0:
    print("FAIL: Initial NPC was modified!")
else:
    print("SUCCESS: Initial NPC preserved.")
