from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from enum import Enum

class Role(str, Enum):
    PRODUCT = "Product"
    DEV = "Dev"
    OPS = "Ops"

class ProjectType(str, Enum):
    GAME = "Game"
    APP = "App"
    INFRA = "Infra"

class ProjectStatus(str, Enum):
    RD = "R&D"
    LIVE = "Live"
    CANCELED = "Canceled"

class Project(BaseModel):
    name: str
    type: ProjectType
    status: ProjectStatus
    difficulty: int
    risk: int
    progress: int = 0
    # bug_count: int = 0  # Deprecated
    revenue: int = 0
    morale: int = 80 # Team Morale
    velocity: int = 10
    quality: int = 70
    scope: int = 100
    deadline: int = 16
    stakeholder_trust: int = 50
    health: int = 75
    confidence: int = 60

class NPC(BaseModel):
    id: str
    name: str
    role: str
    traits: str
    project: str = "General"
    trust: int = 50
    mood: int = 80
    level: str = "P6"
    manager_id: Optional[str] = None
    known: bool = False
    status: str = "在职"
    relations: Dict[str, str] = {}

class Player(BaseModel):
    name: str
    role: Role
    level: str = "P5"  # P5, P6, P7, etc.
    leader_id: Optional[str] = None
    
    # 1. Meta (Innate)
    learning_rate: float = 1.0
    max_energy: int = 100
    
    # 2. Capabilities (Dynamic)
    energy: int = 100
    mood: int = 80
    fatigue: int = 0
    hard_skill: int
    soft_skill: int
    gear_gpu_level: int = 0
    gear_monitor_level: int = 0
    gear_chair_level: int = 0
    
    # 3. Output (Result)
    kpi: int = 0
    political_capital: int = 0
    money: int = 5000
    
    current_project: str
    participated_live_projects: List[str] = []
    launched_projects: List[str] = []
    major_accidents: int = 0
    workbench_purchases: Dict[str, int] = {}
    houses_owned: List[str] = ["starter_rent"]

class GameState(BaseModel):
    player: Optional[Player] = None
    projects: Dict[str, Project] = {}
    npcs: Dict[str, NPC] = {} 
    
    # Time
    week: int = 1
    year: int = 1
    quarter: int = 1
    day_of_week: int = 1 # 1-5 Work, 6-7 Weekend
    
    # Chat History
    chat_history: List[Dict] = []
    workbench_feedback: List[Dict] = []
    context_slots: Dict[str, Dict[str, str]] = {}
    last_topic: str = ""

    global_modifiers: Dict[str, float] = {
        "kpi_multiplier": 1.0,
        "risk_multiplier": 1.0,
        "revenue_multiplier": 1.0,
    }

    memory_facts: List[str] = []
    memory_summary: str = ""
    suggested_replies: List[str] = []
    active_global_event: Optional[Dict] = None
    
    # Flags
    game_over: bool = False
    ending: str = ""
    known_npcs: List[str] = []
    player_subordinates: List[str] = []
    promotion_review: Optional[Dict[str, Any]] = None
    tutorial_reward_claimed: bool = False

class ActionRequest(BaseModel):
    action_type: str # "chat", "workbench"
    content: str 
    target_npc: Optional[str] = None 

class OnboardRequest(BaseModel):
    name: str
    role: Role
    project_name: str
