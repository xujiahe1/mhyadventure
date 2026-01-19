from datetime import datetime
import json
import os
import asyncio
from models import GameState, Player, Project, ProjectType, ProjectStatus, Role, OnboardRequest, NPC
from llm import llm_service
import random
import math
from data.random_events import RANDOM_EVENTS_DB


# Initial Data
INITIAL_PROJECTS = {
    "IAM": Project(name="IAM (Infra)", type=ProjectType.INFRA, status=ProjectStatus.LIVE, difficulty=4, risk=15),
    "Honkai3": Project(name="崩坏3", type=ProjectType.GAME, status=ProjectStatus.LIVE, difficulty=2, risk=10),
    "Genshin": Project(name="原神", type=ProjectType.GAME, status=ProjectStatus.LIVE, difficulty=5, risk=25),
    "HSR": Project(name="星穹铁道", type=ProjectType.GAME, status=ProjectStatus.RD, difficulty=3, risk=15),
    "ZZZ": Project(name="绝区零", type=ProjectType.GAME, status=ProjectStatus.RD, difficulty=4, risk=20),
    "HYG": Project(name="HYG", type=ProjectType.GAME, status=ProjectStatus.RD, difficulty=3, risk=30),
}

def load_all_npcs():
    npcs = {}
    data_path_candidates = [
        os.path.join(os.path.dirname(__file__), "backend/data/npcs.json"),
        os.path.join(os.path.dirname(__file__), "data/npcs.json"),
    ]
    data_path = next((p for p in data_path_candidates if os.path.exists(p)), None)
    
    if data_path and os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                generated_data = json.load(f)
                for npc_id, data in generated_data.items():
                    if npc_id not in npcs:
                        npcs[npc_id] = NPC(**data)
            print(f"Loaded {len(npcs)} NPCs")
        except Exception as e:
            print(f"Error loading configured NPCs: {e}")
    else:
        print("NPC 配置文件未找到。")
    
    return npcs

INITIAL_NPCS = load_all_npcs()

def load_global_events():
    events = []
    data_path_candidates = [
        os.path.join(os.path.dirname(__file__), "backend/data/global_events.json"),
        os.path.join(os.path.dirname(__file__), "data/global_events.json"),
    ]
    data_path = next((p for p in data_path_candidates if os.path.exists(p)), None)

    if data_path and os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                events = json.load(f)
            print(f"Loaded {len(events)} Global Events")
        except Exception as e:
            print(f"Error loading Global Events: {e}")
    else:
        print("Global Events 配置文件未找到。")
    return events

GLOBAL_EVENTS = load_global_events()

RICE_ITEMS = [
    {
        "id": "light",
        "name": "速食简餐",
        "cost": 15,
        "energy": 10,
        "mood": 2,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.1,
        "desc": "你在工位旁边解决了一份速食简餐。"
    },
    {
        "id": "standard",
        "name": "普通套餐",
        "cost": 30,
        "energy": 20,
        "mood": 5,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.15,
        "desc": "你在米饭食堂吃了份普通套餐。"
    },
    {
        "id": "luxury",
        "name": "豪华犒劳",
        "cost": 80,
        "energy": 30,
        "mood": 15,
        "min_level": "P5",
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.3,
        "desc": "你给自己点了一顿豪华犒劳。"
    },
    {
        "id": "midnight",
        "name": "深夜加班餐",
        "cost": 45,
        "energy": 25,
        "mood": -3,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.25,
        "desc": "你在加班间隙随便点了份深夜加班餐。"
    },
    {
        "id": "healthy",
        "name": "健身餐",
        "cost": 55,
        "energy": 18,
        "mood": 6,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.25,
        "desc": "你难得点了一份清爽的健身餐。"
    },
    {
        "id": "salad",
        "name": "减脂沙拉",
        "cost": 40,
        "energy": 8,
        "mood": 4,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.2,
        "desc": "你克制地点了一份减脂沙拉。"
    },
    {
        "id": "spicy",
        "name": "超辣冒菜",
        "cost": 38,
        "energy": 18,
        "mood": 8,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.15,
        "desc": "你挑战了一份超辣冒菜，脑袋都有点清醒了。"
    },
    {
        "id": "buffet",
        "name": "自助餐券",
        "cost": 98,
        "energy": 35,
        "mood": 18,
        "min_level": "P6",
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.4,
        "desc": "你拿着自助餐券干饭，顺便和同事聊了不少。"
    },
    {
        "id": "afternoon_tea",
        "name": "下午茶点心",
        "cost": 28,
        "energy": 6,
        "mood": 10,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.15,
        "desc": "你和同事拼单了一份下午茶点心。"
    },
    {
        "id": "breakfast_combo",
        "name": "早餐大礼包",
        "cost": 25,
        "energy": 15,
        "mood": 5,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.2,
        "desc": "你早起吃了一份完整的早餐大礼包。"
    },
    {
        "id": "late_snack",
        "name": "夜宵炸鸡",
        "cost": 42,
        "energy": 16,
        "mood": 12,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.1,
        "desc": "你和项目组一起拼了份夜宵炸鸡。"
    },
    {
        "id": "team_lunch",
        "name": "项目组团建午餐",
        "cost": 65,
        "energy": 20,
        "mood": 15,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.3,
        "limit": 3,
        "desc": "你和项目组一起出去吃了顿团建午餐。"
    },
    {
        "id": "hidden_menu",
        "name": "食堂隐藏菜单",
        "cost": 32,
        "energy": 22,
        "mood": 8,
        "min_level": "P5",
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.25,
        "limit": 2,
        "desc": "你解锁了食堂大妈只对熟人开放的隐藏菜单。"
    },
    {
        "id": "fruit_plate",
        "name": "办公室水果拼盘",
        "cost": 30,
        "energy": 8,
        "mood": 10,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.2,
        "desc": "你点了一份办公室水果拼盘，感觉清爽不少。"
    },
    {
        "id": "brain_soup",
        "name": "养生鸡汤",
        "cost": 36,
        "energy": 18,
        "mood": 8,
        "min_level": "P5",
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.35,
        "desc": "你喝了一碗热腾腾的养生鸡汤。"
    },
    {
        "id": "congee",
        "name": "养胃小米粥",
        "cost": 18,
        "energy": 12,
        "mood": 6,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.2,
        "desc": "你点了一碗暖胃的小米粥。"
    },
    {
        "id": "ramen",
        "name": "深夜拉面",
        "cost": 35,
        "energy": 18,
        "mood": 9,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.25,
        "desc": "你在公司楼下吃了一碗热乎乎的拉面。"
    },
    {
        "id": "bento",
        "name": "自带便当",
        "cost": 0,
        "energy": 14,
        "mood": 7,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.3,
        "desc": "你吃掉了精心准备的自带便当。"
    },
    {
        "id": "mystery_meal",
        "name": "神秘今日特餐",
        "cost": 33,
        "energy": 16,
        "mood": 6,
        "min_level": "P5",
        "learning_rate_delta": 0.15,
        "learning_rate_chance": 0.3,
        "desc": "你点了一份厨师推荐的神秘特餐。"
    },
    {
        "id": "brain_buffet",
        "name": "脑力自助餐",
        "cost": 120,
        "energy": 28,
        "mood": 18,
        "min_level": "P6",
        "learning_rate_delta": 0.2,
        "learning_rate_chance": 1.0,
        "limit": 2,
        "desc": "你参加了公司请客的脑力自助餐交流会。"
    },
    {
        "id": "cheap_snack",
        "name": "办公零食凑合吃",
        "cost": 10,
        "energy": 6,
        "mood": 3,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.1,
        "desc": "你翻出了抽屉里的办公零食，凑合顶了一顿。"
    },
]

SHOP_ITEMS = [
    {
        "id": "gift",
        "name": "限量手办礼物",
        "cost": 200,
        "min_level": "P5",
        "limit": 5,
        "desc": "你在米购下单了一份限量手办礼物。"
    },
    {
        "id": "gpu",
        "name": "显卡升级",
        "cost": 3000,
        "min_level": "P5",
        "desc": "你在米购购买了一块新显卡。"
    },
    {
        "id": "monitor",
        "name": "显示器升级",
        "cost": 2000,
        "min_level": "P5",
        "desc": "你在米购换上了新的高刷显示器。"
    },
    {
        "id": "chair",
        "name": "工学椅升级",
        "cost": 1500,
        "min_level": "P5",
        "desc": "你在米购入手了一把人体工学椅。"
    },
    {
        "id": "coffee_pass",
        "name": "咖啡月卡",
        "cost": 260,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.5,
        "limit": 2,
        "desc": "你购买了咖啡月卡，头脑似乎更清醒了。"
    },
    {
        "id": "snack_box",
        "name": "零食补给箱",
        "cost": 120,
        "min_level": "P5",
        "mood": 10,
        "desc": "你为工位备了一整箱零食。"
    },
    {
        "id": "massage_coupon",
        "name": "按摩理疗券",
        "cost": 180,
        "min_level": "P5",
        "energy": 20,
        "mood": 8,
        "desc": "你预约了一次肩颈按摩。"
    },
    {
        "id": "noise_headphone",
        "name": "降噪耳机",
        "cost": 2200,
        "min_level": "P5",
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.8,
        "desc": "你买了一副降噪耳机，专注度明显提高。"
    },
    {
        "id": "standing_desk",
        "name": "升降桌",
        "cost": 2800,
        "min_level": "P6",
        "energy": 10,
        "mood": 6,
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.4,
        "desc": "你升级成了可以站着写代码的升降桌。"
    },
    {
        "id": "plant",
        "name": "工位绿植",
        "cost": 60,
        "min_level": "P5",
        "mood": 6,
        "desc": "你在工位摆了一盆小绿植。"
    },
    {
        "id": "keyboard",
        "name": "机械键盘",
        "cost": 700,
        "min_level": "P5",
        "mood": 5,
        "desc": "你换上了有敲击手感的机械键盘。"
    },
    {
        "id": "mouse",
        "name": "人体工学鼠标",
        "cost": 350,
        "min_level": "P5",
        "energy": 5,
        "desc": "你换上了更顺手的人体工学鼠标。"
    },
    {
        "id": "desk_lamp",
        "name": "护眼台灯",
        "cost": 280,
        "min_level": "P5",
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.4,
        "desc": "你在工位添置了一盏护眼台灯。"
    },
    {
        "id": "book_pack_hard",
        "name": "硬核技术书单",
        "cost": 400,
        "min_level": "P5",
        "hard_skill": 2,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.7,
        "desc": "你在米购买了一套硬核技术书单。"
    },
    {
        "id": "book_pack_soft",
        "name": "管理沟通书单",
        "cost": 380,
        "min_level": "P5",
        "soft_skill": 2,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.7,
        "desc": "你在米购买了一套沟通与管理书单。"
    },
    {
        "id": "cloud_subscription",
        "name": "云服务订阅",
        "cost": 520,
        "min_level": "P5",
        "hard_skill": 1,
        "desc": "你为个人项目开通了一些云服务额度。"
    },
    {
        "id": "ai_toolkit",
        "name": "AI 助手工具包",
        "cost": 980,
        "min_level": "P6",
        "hard_skill": 1,
        "soft_skill": 1,
        "learning_rate_delta": 0.15,
        "learning_rate_chance": 1.0,
        "limit": 1,
        "desc": "你采购了一套 AI 辅助工具集。"
    },
    {
        "id": "team_snack",
        "name": "团队下午茶",
        "cost": 260,
        "min_level": "P5",
        "mood": 15,
        "political_capital": 2,
        "limit": 3,
        "desc": "你给项目组买了整套下午茶。"
    },
    {
        "id": "lucky_draw",
        "name": "盲盒福袋",
        "cost": 66,
        "min_level": "P5",
        "learning_rate_delta": 0.2,
        "learning_rate_chance": 0.3,
        "mood": 10,
        "desc": "你买了一个盲盒福袋，结果出乎意料地好。"
    },
    {
        "id": "vip_gym",
        "name": "健身房年卡",
        "cost": 1800,
        "min_level": "P6",
        "energy": 10,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.6,
        "desc": "你为自己办了一张健身房年卡。"
    },
]

ACADEMY_COURSES = [
    {
        "id": "base",
        "name": "基础进阶课",
        "cost": 100,
        "energy_cost": 30,
        "min_level": "P5",
        "hard_skill": 0,
        "soft_skill": 0,
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.6,
        "desc": "你在米忽悠学院报了一门基础进阶课。"
    },
    {
        "id": "hard_camp",
        "name": "硬核技术训练营",
        "cost": 200,
        "energy_cost": 40,
        "min_level": "P5",
        "hard_skill": 4,
        "soft_skill": 0,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.8,
        "desc": "你在米忽悠学院参加了硬核技术训练营。"
    },
    {
        "id": "soft_workshop",
        "name": "沟通协作工作坊",
        "cost": 200,
        "energy_cost": 30,
        "min_level": "P5",
        "hard_skill": 0,
        "soft_skill": 4,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.8,
        "desc": "你在米忽悠学院参加了沟通协作工作坊。"
    },
    {
        "id": "leadership",
        "name": "项目管理与领导力",
        "cost": 300,
        "energy_cost": 35,
        "min_level": "P6",
        "hard_skill": 0,
        "soft_skill": 2,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.7,
        "desc": "你在米忽悠学院完成了项目管理与领导力课程。"
    },
    {
        "id": "architecture",
        "name": "系统架构设计实战",
        "cost": 280,
        "energy_cost": 35,
        "min_level": "P6",
        "hard_skill": 3,
        "soft_skill": 1,
        "learning_rate_delta": 0.15,
        "learning_rate_chance": 0.8,
        "desc": "你参加了系统架构设计实战营。"
    },
    {
        "id": "performance",
        "name": "性能优化与压测",
        "cost": 260,
        "energy_cost": 35,
        "min_level": "P5",
        "hard_skill": 3,
        "soft_skill": 0,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.7,
        "desc": "你系统学习了性能优化与压测。"
    },
    {
        "id": "product_sense",
        "name": "产品感与体验设计",
        "cost": 220,
        "energy_cost": 30,
        "min_level": "P5",
        "hard_skill": 0,
        "soft_skill": 3,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.7,
        "desc": "你听完了一整套产品体验设计课程。"
    },
    {
        "id": "data_analysis",
        "name": "数据分析与指标体系",
        "cost": 240,
        "energy_cost": 30,
        "min_level": "P5",
        "hard_skill": 2,
        "soft_skill": 1,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.7,
        "desc": "你完成了数据分析与指标体系课程。"
    },
    {
        "id": "negotiation",
        "name": "跨部门协同与谈判",
        "cost": 260,
        "energy_cost": 35,
        "min_level": "P6",
        "hard_skill": 0,
        "soft_skill": 3,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.7,
        "desc": "你学习了如何跟其他部门高效对齐。"
    },
    {
        "id": "review_skill",
        "name": "复盘与总结能力",
        "cost": 180,
        "energy_cost": 25,
        "min_level": "P5",
        "hard_skill": 1,
        "soft_skill": 2,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.8,
        "desc": "你学习了如何做系统复盘与总结。"
    },
    {
        "id": "writing",
        "name": "文档与写作训练",
        "cost": 160,
        "energy_cost": 20,
        "min_level": "P5",
        "hard_skill": 1,
        "soft_skill": 1,
        "learning_rate_delta": 0.05,
        "learning_rate_chance": 0.8,
        "desc": "你训练了自己写文档和表达的能力。"
    },
    {
        "id": "ai_course",
        "name": "AI 应用实践营",
        "cost": 320,
        "energy_cost": 40,
        "min_level": "P6",
        "hard_skill": 3,
        "soft_skill": 1,
        "learning_rate_delta": 0.2,
        "learning_rate_chance": 1.0,
        "desc": "你报名了 AI 应用实践营。"
    },
    {
        "id": "mentor_clinic",
        "name": "导师一对一诊室",
        "cost": 260,
        "energy_cost": 25,
        "min_level": "P6",
        "hard_skill": 1,
        "soft_skill": 2,
        "learning_rate_delta": 0.15,
        "learning_rate_chance": 0.8,
        "limit": 3,
        "desc": "你约了资深导师做一对一职业诊断。"
    },
    {
        "id": "presentation",
        "name": "演讲与汇报训练营",
        "cost": 230,
        "energy_cost": 30,
        "min_level": "P5",
        "hard_skill": 0,
        "soft_skill": 3,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.8,
        "desc": "你参加了演讲与汇报训练营。"
    },
    {
        "id": "team_building",
        "name": "带团队实战营",
        "cost": 340,
        "energy_cost": 40,
        "min_level": "P7",
        "hard_skill": 1,
        "soft_skill": 3,
        "learning_rate_delta": 0.15,
        "learning_rate_chance": 1.0,
        "desc": "你体验了一次完整的项目带队实战营。"
    },
    {
        "id": "career_design",
        "name": "职业路径设计课",
        "cost": 220,
        "energy_cost": 25,
        "min_level": "P5",
        "hard_skill": 0,
        "soft_skill": 2,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.9,
        "desc": "你认真规划了自己的职业路径。"
    },
    {
        "id": "startup_mind",
        "name": "创业思维与商业模型",
        "cost": 260,
        "energy_cost": 35,
        "min_level": "P6",
        "hard_skill": 2,
        "soft_skill": 2,
        "learning_rate_delta": 0.15,
        "learning_rate_chance": 1.0,
        "desc": "你学习了创业思维与商业模型。"
    },
    {
        "id": "game_design",
        "name": "游戏策划与数值设计",
        "cost": 260,
        "energy_cost": 35,
        "min_level": "P5",
        "hard_skill": 2,
        "soft_skill": 1,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.8,
        "desc": "你上完了一套游戏策划与数值设计课程。"
    },
    {
        "id": "ops_system",
        "name": "运营体系与活动设计",
        "cost": 220,
        "energy_cost": 30,
        "min_level": "P5",
        "hard_skill": 1,
        "soft_skill": 2,
        "learning_rate_delta": 0.1,
        "learning_rate_chance": 0.8,
        "desc": "你学习了完整的运营体系与活动设计。"
    },
    {
        "id": "random_inspiration",
        "name": "灵感涌现工作坊",
        "cost": 200,
        "energy_cost": 25,
        "min_level": "P5",
        "hard_skill": 1,
        "soft_skill": 1,
        "learning_rate_delta": 0.2,
        "learning_rate_chance": 0.4,
        "desc": "你参加了一个脑洞大开的灵感工作坊。"
    },
]

class GameManager:
    def __init__(self):
        self.state = GameState()
        # Deep copy initial data to avoid reference issues on reset
        self.state.projects = {k: v.model_copy(deep=True) for k, v in INITIAL_PROJECTS.items()}
        self.state.npcs = {k: v.model_copy(deep=True) for k, v in INITIAL_NPCS.items()}
        self.state.known_npcs = []
        self.state.player_subordinates = []
        self._init_npc_relations()

    def _init_npc_relations(self):
        project_groups = {}
        for npc_id, npc in self.state.npcs.items():
            if not npc_id.startswith("NPC_"):
                continue
            existing_relations = getattr(npc, "relations", None) or {}
            if existing_relations:
                continue
            project_key = npc.project or "General"
            if project_key not in project_groups:
                project_groups[project_key] = []
            project_groups[project_key].append(npc_id)

        for project_key, ids in project_groups.items():
            if len(ids) < 2:
                continue
            random.shuffle(ids)
            pair_count = max(1, len(ids) // 4)
            for _ in range(pair_count):
                a_id, b_id = random.sample(ids, 2)
                a = self.state.npcs.get(a_id)
                b = self.state.npcs.get(b_id)
                if not a or not b:
                    continue
                a_rel = getattr(a, "relations", None) or {}
                if b_id in a_rel:
                    continue
                if self._should_be_rivals(a, b):
                    label = "对立"
                else:
                    label = "合作"
                new_a_rel = dict(a_rel)
                b_rel = getattr(b, "relations", None) or {}
                new_b_rel = dict(b_rel)
                new_a_rel[b_id] = label
                new_b_rel[a_id] = label
                a.relations = new_a_rel
                b.relations = new_b_rel

    def _should_be_rivals(self, npc_a, npc_b) -> bool:
        roles = {npc_a.role, npc_b.role}
        traits_text = (npc_a.traits or "") + (npc_b.traits or "")
        tough_keywords = ["毒舌", "强硬", "零容忍"]
        has_tough = any(k in traits_text for k in tough_keywords)
        cross_role = "Dev" in roles and "Product" in roles
        same_project = npc_a.project == npc_b.project and npc_a.project not in ("", "General")
        high_level = self._parse_level(npc_a.level) >= 7 or self._parse_level(npc_b.level) >= 7
        if cross_role and same_project and has_tough:
            return True
        if same_project and has_tough and high_level:
            return True
        return False

    def _parse_level(self, level: str) -> int:
        try:
            return int(str(level).replace("P", ""))
        except Exception:
            return 5

    def _is_executive(self, npc) -> bool:
        level_num = self._parse_level(getattr(npc, "level", "P5"))
        role_text = str(getattr(npc, "role", "") or "")
        name_text = str(getattr(npc, "name", "") or "")
        traits_text = str(getattr(npc, "traits", "") or "")
        keywords = ["总裁", "CTO", "创始人", "负责人", "Head"]
        has_keyword = any(k in role_text or k in name_text or k in traits_text for k in keywords)
        return level_num >= 9 or has_keyword

    def _get_top_executives_ids(self) -> list:
        exec_ids = [
            nid for nid, npc in self.state.npcs.items()
            if getattr(npc, "status", "在职") == "在职" and self._is_executive(npc)
        ]
        exec_ids.sort(
            key=lambda nid: (
                self._parse_level(self.state.npcs[nid].level),
                getattr(self.state.npcs[nid], "trust", 0)
            ),
            reverse=True
        )
        return exec_ids[:5]

    async def _safe_call(self, coro):
        try:
            await coro
        except Exception:
            return

    async def _try_generate_welcome(self, req: OnboardRequest, leader):
        try:
            welcome_text = await asyncio.wait_for(
                llm_service.generate_welcome(
                    player_name=req.name,
                    player_role=req.role.value,
                    project_name=req.project_name,
                    leader_name=leader.name,
                    leader_role=leader.role,
                    leader_traits=leader.traits
                ),
                timeout=6.0
            )
            if welcome_text:
                self.state.chat_history.append({
                    "sender": leader.name, 
                    "content": welcome_text,
                    "type": "npc",
                    "target": "group",
                    "timestamp": self._get_timestamp()
                })
        except Exception:
            return

    def _get_timestamp(self) -> str:
        return datetime.now().isoformat()

    def _add_fact(self, fact: str):
        fact = (fact or "").strip()
        if not fact:
            return
        if fact in self.state.memory_facts:
            return
        self.state.memory_facts.append(fact)
        if len(self.state.memory_facts) > 20:
            self.state.memory_facts = self.state.memory_facts[-20:]

    def _advance_time(self, channel: str, weeks: int = 1, days: int = 0, global_event_prob: float = None):
        if not self.state.player:
            return

        # Fast Paced: Treat any time advance as at least 1 week
        total_weeks = weeks
        if days > 0:
            # If legacy days provided, treat as weeks or convert
            total_weeks += max(1, int(days / 7))
            if total_weeks == 0 and days > 0:
                total_weeks = 1

        for _ in range(total_weeks):
            self.state.week += 1
            
            # Update Year/Quarter (1 Year = 48 Weeks, 1 Quarter = 12 Weeks)
            w = self.state.week
            self.state.year = ((w - 1) // 48) + 1
            self.state.quarter = (((w - 1) // 12) % 4) + 1

            self._weekly_tick(channel)

            if (self.state.week - 1) % 12 == 0:
                self._maybe_quarterly_event(channel)
            
            if (self.state.week - 1) % 48 == 0:
                self._maybe_new_project(channel)

        self._maybe_global_event(channel, base_prob_override=global_event_prob)

    def _mark_npc_known(self, npc_id: str):
        if not npc_id or npc_id not in self.state.npcs:
            return
        npc = self.state.npcs[npc_id]
        npc.known = True
        if npc_id not in self.state.known_npcs:
            self.state.known_npcs.append(npc_id)

    def _maybe_global_event(self, channel: str, base_prob_override: float = None):
        if not self.state.player:
            return
        if self.state.active_global_event:
            return
        player = self.state.player
        project = self.state.projects.get(player.current_project)
        week = self.state.week
        mood = player.mood
        energy = player.energy
        candidates = []
        for ev in GLOBAL_EVENTS:
            min_week = ev.get("min_week")
            if min_week is not None and week < min_week:
                continue
            max_week = ev.get("max_week")
            if max_week is not None and week > max_week:
                continue
            min_mood = ev.get("min_mood")
            if min_mood is not None and mood < min_mood:
                continue
            max_mood = ev.get("max_mood")
            if max_mood is not None and mood > max_mood:
                continue
            min_energy = ev.get("min_energy")
            if min_energy is not None and energy < min_energy:
                continue
            max_energy = ev.get("max_energy")
            if max_energy is not None and energy > max_energy:
                continue
            if ev["type"] == "project" and not project:
                continue
            candidates.append(ev)
        if not candidates:
            return
        if base_prob_override is not None:
            base_prob = base_prob_override
        else:
            base_prob = 0.08
            if mood <= 25:
                base_prob += 0.12
            if energy <= 25:
                base_prob += 0.12
            if project and project.risk >= 80:
                base_prob += 0.1
        if random.random() > base_prob:
            return
        ev = random.choice(candidates)
        self._activate_global_event(ev, channel)

    def _activate_global_event(self, ev: dict, channel: str):
        if not self.state.player:
            return
        player = self.state.player
        project = self.state.projects.get(player.current_project)
        event_state = {
            "id": ev["id"],
            "title": ev["title"],
            "description": ev["description"],
            "type": ev.get("type", "generic")
        }
        self.state.active_global_event = event_state
        effect = ev.get("effect")
        if effect == "hospital_quarter":
            lost_weeks = 12
            self.state.week += lost_weeks
            player.energy = min(player.max_energy, player.energy + 40)
            player.mood = max(0, min(100, player.mood - 10))
            player.money -= 3000
            msg = f"{ev['title']}：你住院休养了一个季度，时间悄然流逝，医疗支出增加。"
            self._add_fact("住院休养一个季度")
        elif effect == "short_sick_leave":
            player.energy = max(0, player.energy - 10)
            player.mood = max(0, min(100, player.mood + 10))
            msg = f"{ev['title']}：你被迫在家休息几天，身体稍微恢复了一些。"
        elif effect == "health_check_bonus":
            player.mood = max(0, min(100, player.mood + 8))
            player.energy = min(player.max_energy, player.energy + 10)
            msg = f"{ev['title']}：你做了全面体检并体验SPA，状态有所恢复。"
        elif effect == "all_hands_meeting":
            msg = f"{ev['title']}：你整天泡在大会里，项目进度被迫暂停。"
        elif effect == "fire_drill":
            player.energy = max(0, player.energy - 5)
            msg = f"{ev['title']}：跑楼梯和集合让你有点累，但也顺便活动了筋骨。"
        elif effect == "team_building":
            player.mood = max(0, min(100, player.mood + 12))
            if project:
                project.morale = max(0, min(100, project.morale + 8))
            msg = f"{ev['title']}：团建让团队关系更近了一些，但节奏被打乱。"
        elif effect == "audit_week":
            player.mood = max(0, player.mood - 8)
            msg = f"{ev['title']}：大量表格和说明文档让你身心俱疲。"
        elif effect == "project_review":
            if project:
                project.risk = max(0, min(100, project.risk - 5))
            player.political_capital = max(0, player.political_capital + 3)
            msg = f"{ev['title']}：你在评审会上稳定发挥，为项目争取到了一些支持。"
        elif effect == "outage_pause":
            if project:
                project.risk = max(0, min(100, project.risk + 5))
            msg = f"{ev['title']}：系统停机期间，大部分计划工作被迫延后。"
        elif effect == "security_response":
            if project:
                project.risk = max(0, min(100, project.risk - 3))
                # project.bug_count = max(0, project.bug_count - 5)
                pass
            player.hard_skill += 1
            msg = f"{ev['title']}：你参与了安全加固行动，对系统有了更深理解。"
        elif effect == "version_freeze":
            msg = f"{ev['title']}：开发节奏放缓，你有时间整理文档和技术债。"
        elif effect == "family_leave":
            player.mood = max(0, min(100, player.mood - 5))
            msg = f"{ev['title']}：你抽身处理家庭事务，工作暂时靠同事兜底。"
        elif effect == "house_move":
            player.energy = max(0, player.energy - 10)
            player.mood = max(0, min(100, player.mood + 5))
            msg = f"{ev['title']}：搬家很累，但通勤距离缩短让你稍微开心了一些。"
        elif effect == "marathon_event":
            player.energy = max(0, player.energy - 15)
            player.mood = max(0, min(100, player.mood + 8))
            msg = f"{ev['title']}：体力被掏空，但完成马拉松让你很有成就感。"
        elif effect == "exam_study":
            player.money -= 800
            player.hard_skill += 1
            player.soft_skill += 1
            msg = f"{ev['title']}：报班与考试费用让你肉疼，但能力有所提升。"
        elif effect == "stock_up":
            player.money += 3000
            msg = f"{ev['title']}：理财收益到账，你心情愉悦了一整周。"
        elif effect == "bonus_rain":
            player.money += 8000
            player.political_capital = max(0, player.political_capital + 2)
            msg = f"{ev['title']}：项目激励入账，你的存在感也随之提升。"
        elif effect == "celebration_party":
            player.mood = max(0, min(100, player.mood + 6))
            player.energy = max(0, player.energy - 8)
            msg = f"{ev['title']}：庆功宴很嗨，但第二天上班有点吃力。"
        elif effect == "commute_disaster":
            player.energy = max(0, player.energy - 10)
            player.mood = max(0, player.mood - 5)
            msg = f"{ev['title']}：通勤时间翻倍，你每天都在地铁和路上消耗精力。"
        elif effect == "rain_week":
            player.mood = max(0, player.mood - 4)
            msg = f"{ev['title']}：阴雨天气让你的工作状态也有些低气压。"
        elif effect == "bug_storm":
            if project:
                # project.bug_count = max(0, project.bug_count + 15)
                project.risk = max(0, min(100, project.risk + 5))
            msg = f"{ev['title']}：你被卷入接连不断的Bug风暴，压力陡增。"
        elif effect == "org_restructure":
            self._add_fact("组织调整")
            player.political_capital = max(0, player.political_capital + 3)
            msg = f"{ev['title']}：组织调整中，你努力保持中立并维护关键关系。"
        elif effect == "policy_change":
            msg = f"{ev['title']}：新的制度生效，你需要重新找到工作与生活的平衡。"
        elif effect == "tool_rollout":
            player.hard_skill += 1
            msg = f"{ev['title']}：你主动研究新工具，逐渐变成团队里的“工具管理员”。"
        elif effect == "mentor_assigned":
            player.soft_skill += 2
            msg = f"{ev['title']}：在导师的指导下，你开始系统思考自己的职业发展。"
        elif effect == "internal_share":
            player.soft_skill += 1
            player.political_capital = max(0, player.political_capital + 2)
            msg = f"{ev['title']}：内部分享让更多人认识了你，你的影响力有所提升。"
        elif effect == "interview_panel":
            player.soft_skill += 1
            msg = f"{ev['title']}：面试候选人的过程让你学会从团队视角看问题。"
        elif effect == "cross_team_project":
            player.soft_skill += 1
            self._add_fact("跨部门项目经验")
            msg = f"{ev['title']}：跨团队协作拓宽了你的人脉与视野。"
        elif effect == "summit_invite":
            player.hard_skill += 1
            player.soft_skill += 1
            msg = f"{ev['title']}：行业峰会带来大量新知识与人脉，你受益匪浅。"
        elif effect == "ai_strategy_night":
            player.energy = max(0, player.energy - 25)
            player.mood = max(0, player.mood - 5)
            if project:
                project.risk = max(0, min(100, project.risk - 5))
            msg = f"{ev['title']}：你通宵跟着讨论 AI 战略，大饼画满白板，项目暂时获得了一些资源承诺。"
        elif effect == "ip_crossover_crunch":
            if project:
                project.progress = max(0, min(200, project.progress + 15))
                project.risk = max(0, min(100, project.risk + 10))
            player.energy = max(0, player.energy - 20)
            msg = f"{ev['title']}：你连夜赶工联动内容，进度暴涨但技术债也随之堆积。"
        elif effect == "streamer_viral":
            player.mood = max(0, min(100, player.mood + 12))
            player.political_capital = max(0, player.political_capital + 4)
            msg = f"{ev['title']}：你的直播出圈，被官方当成宣传案例，你的存在感大幅提升。"
        elif effect == "all_in_invest":
            delta = random.randint(-5000, 8000)
            player.money += delta
            mood_delta = 8 if delta > 0 else -8
            player.mood = max(0, min(100, player.mood + mood_delta))
            msg = f"{ev['title']}：二次元赛道剧烈波动，你的账户{'暴涨' if delta>0 else '回撤'}了 {abs(delta)}，心情随之大起大落。"
        elif effect == "internet_maintenance":
            player.energy = max(0, player.energy - 8)
            if project:
                project.progress = max(0, project.progress - 5)
            msg = f"{ev['title']}：网络持续抽风，开发与提测节奏被全面打乱。"
        elif effect == "burnout_break":
            lost_weeks = 4
            self.state.week += lost_weeks
            player.energy = min(player.max_energy, player.energy + 30)
            player.mood = max(0, min(100, player.mood - 5))
            player.money -= 1000
            msg = f"{ev['title']}：你被安排强制休整了一个月，收入略受影响，但总算没有彻底燃尽。"
            self._add_fact("经历职业倦怠预警并被强制休整")
        else:
            msg = f"{ev['title']}：{ev['description']}"
        self.state.chat_history.append({
            "sender": "System",
            "content": msg,
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })

    def _infer_intent_magnitude(self, text: str):
        t = (text or "").lower()

        def has_any(words):
            return any(w in t for w in words)

        intent = "SMALL_TALK"
        if has_any(["加班", "爆肝", "肝", "工作", "修bug", "修复", "debug", "写代码", "改需求", "推进"]):
            intent = "WORK"
        elif has_any(["摸鱼", "休息", "摆烂", "躺平"]):
            intent = "REFUSE"
        elif has_any(["买", "吃", "喝", "外卖", "奶茶", "咖啡", "点餐"]):
            intent = "SHOP"
        elif has_any(["学习", "培训", "上课", "复盘", "读文档"]):
            intent = "LEARN"
        elif has_any(["打", "骂", "滚", "傻", "废物", "操", "你妈"]):
            intent = "ATTACK"

        magnitude = 1.0
        if intent == "SMALL_TALK":
            magnitude = 0.4
        elif has_any(["通宵", "爆肝", "肝爆", "死磕"]):
            magnitude = 1.6
        elif has_any(["稍微", "一点", "小加班"]):
            magnitude = 0.8
        elif has_any(["加班", "努力", "认真"]):
            magnitude = 1.2

        return intent, magnitude

    def _weekly_tick(self, channel: str):
        player = self.state.player
        project = self.state.projects.get(player.current_project) if player else None
        
        # 1. Living Cost & Salary
        if player:
            living_cost = 300 # Weekly rent & food
            
            # Weekly Salary based on Level
            level_num = self._parse_level(player.level)
            base_salary = 500 + (level_num - 5) * 200 # P5=500, P6=700, P7=900...
            salary = int(base_salary * self.state.global_modifiers.get("revenue_multiplier", 1.0))
            
            player.money += (salary - living_cost)
            
            if player.money < 0:
                # Can go into debt slightly before Game Over check catches it
                pass

        if project:
            # bug_growth = max(0, int(project.difficulty / 2))
            # project.bug_count = max(0, project.bug_count + bug_growth)
            risk_growth = max(0, int(math.ceil(project.difficulty * 0.5)))
            project.risk = max(0, min(100, project.risk + risk_growth))
            project.morale = max(0, min(100, project.morale - 1))
            if project.status == ProjectStatus.LIVE:
                base_week_rev = int(800 * project.difficulty * self.state.global_modifiers.get("revenue_multiplier", 1.0))
                trust_factor = 0.5 + 0.5 * (project.stakeholder_trust / 100.0)
                potential_gain = int(base_week_rev * trust_factor)
                target = self._project_revenue_target(project)
                if project.revenue < target:
                    remaining = max(0, target - project.revenue)
                    gain = min(potential_gain, remaining)
                    project.revenue = project.revenue + gain
                if project.stakeholder_trust >= 70 and project.morale >= 60:
                    project.risk = max(0, project.risk - 2)
                elif project.stakeholder_trust >= 50 and project.morale >= 50:
                    project.risk = max(0, project.risk - 1)
                elif project.stakeholder_trust <= 30:
                    project.risk = min(100, project.risk + 1)
            trust_delta = 0
            if project.risk >= 80:
                trust_delta -= 2
            elif project.risk >= 60:
                trust_delta -= 1
            # if project.bug_count >= 50:
            #     trust_delta -= 1
            if trust_delta != 0:
                project.stakeholder_trust = max(0, min(100, project.stakeholder_trust + trust_delta))

        if player and project and project.status == ProjectStatus.LIVE:
            if player.current_project not in player.participated_live_projects:
                player.participated_live_projects.append(player.current_project)

        if player and project and project.risk >= 90:
            player.major_accidents = max(0, player.major_accidents + 1)
            self.state.chat_history.append({
                "sender": "System",
                "content": f"{project.name} 出现重大风险（Risk {project.risk}/100）。",
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            })
            self._add_fact(f"重大事故 {project.name} 第{self.state.week}周")

        self._npc_ecology_tick(channel)
        self._project_evolution_tick(channel)
        self._check_promotion(channel)
        self._check_game_over(channel)

    def _npc_ecology_tick(self, channel: str):
        player = self.state.player
        if not player or not self.state.npcs:
            return

        candidate_ids = set(self.state.known_npcs or [])
        for sid in self.state.player_subordinates or []:
            candidate_ids.add(sid)

        if not candidate_ids:
            return

        projects = list(self.state.projects.keys())

        for npc_id in candidate_ids:
            npc = self.state.npcs.get(npc_id)
            if not npc or getattr(npc, "status", "在职") != "在职":
                continue

            npc_project_state = self.state.projects.get(getattr(npc, "project", ""), None)

            base_prob = 0.02
            if npc.mood <= 40:
                base_prob += 0.04
            if npc.trust <= 30:
                base_prob += 0.03
            if npc_project_state and npc_project_state.risk >= 70:
                base_prob += 0.05

            relations = getattr(npc, "relations", None) or {}
            relation_candidates = []
            for other_id, relation_label in relations.items():
                other = self.state.npcs.get(other_id)
                if not other or getattr(other, "status", "在职") != "在职":
                    continue
                relation_candidates.append((other_id, relation_label))

            if relation_candidates:
                relation_prob = base_prob + 0.03
                if npc_project_state and npc_project_state.risk >= 70:
                    relation_prob += 0.03
                if self._parse_level(npc.level) >= 7:
                    relation_prob += 0.02
                if random.random() < relation_prob:
                    self._trigger_relation_event(npc, relation_candidates, channel, player)
                    continue

            if random.random() > base_prob:
                continue

            resign_weight = 0.4
            transfer_weight = 0.35
            promote_weight = 0.25

            level_num = self._parse_level(npc.level)
            if npc_project_state and npc_project_state.risk >= 70:
                resign_weight += 0.15
                transfer_weight += 0.1
                promote_weight -= 0.05
            if level_num >= 7:
                promote_weight += 0.15
                resign_weight -= 0.05

            event_type = random.choices(
                ["resign", "transfer", "promote"],
                weights=[resign_weight, transfer_weight, promote_weight]
            )[0]

            if event_type == "resign":
                npc.status = "已离职"
                if npc_id in self.state.player_subordinates:
                    self.state.player_subordinates = [
                        sid for sid in self.state.player_subordinates if sid != npc_id
                    ]
                    player.mood = max(0, player.mood - 5)
                msg = f"{npc.name} 提交了离职申请，正式离开公司。"
            elif event_type == "transfer":
                if not projects:
                    continue
                current_project = npc.project
                target_candidates = [p for p in projects if p != current_project]
                if not target_candidates:
                    continue
                new_project = random.choice(target_candidates)
                npc.project = new_project
                if npc_id in self.state.player_subordinates and new_project != player.current_project:
                    self.state.player_subordinates = [
                        sid for sid in self.state.player_subordinates if sid != npc_id
                    ]
                    player.mood = max(0, player.mood - 3)
                msg = f"{npc.name} 申请内部转岗，调往 {new_project} 项目组。"
            else:
                if level_num >= 10:
                    continue
                npc.level = f"P{level_num + 1}"
                npc.trust = min(100, npc.trust + 5)
                msg = f"{npc.name} 获得晋升，职级提升为 {npc.level}。"

            self.state.chat_history.append({
                "sender": "System",
                "content": msg,
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            })

    def _trigger_relation_event(self, npc, relation_candidates, channel: str, player: Player):
        other_id, relation_label = random.choice(relation_candidates)
        other = self.state.npcs.get(other_id)
        if not other or getattr(other, "status", "在职") != "在职":
            return
        project_name = npc.project or other.project or "General"
        text = relation_label or ""
        conflict = "对立" in text or "冲突" in text
        if conflict:
            npc.mood = max(0, npc.mood - 4)
            other.mood = max(0, other.mood - 4)
            if player and (npc.project == player.current_project or other.project == player.current_project):
                player.mood = max(0, player.mood - 2)
            msg = f"{npc.name} 与 {other.name} 在 {project_name} 项目上再次针锋相对，群里气氛瞬间凝固。"
        else:
            npc.mood = min(100, npc.mood + 3)
            other.mood = min(100, other.mood + 3)
            if player and project_name == player.current_project:
                player.mood = min(100, player.mood + 1)
            msg = f"{npc.name} 与 {other.name} 在 {project_name} 项目上相互补位，配合得十分默契。"
        self._mark_npc_known(other_id)
        self.state.chat_history.append({
            "sender": "System",
            "content": msg,
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })

    def _maybe_quarterly_event(self, channel: str):
        if self.state.week % 12 != 0:
            return

        events = [
            {
                "title": "版号收紧",
                "kpi_multiplier": 0.9,
                "risk_multiplier": 1.1,
                "revenue_multiplier": 0.9,
                "msg": "版号环境变紧：整体风险上升，产出效率下降。",
            },
            {
                "title": "新品类风口",
                "kpi_multiplier": 1.1,
                "risk_multiplier": 1.0,
                "revenue_multiplier": 1.15,
                "msg": "新品类风口出现：资源倾斜，营收预期提升。",
            },
            {
                "title": "大促季",
                "kpi_multiplier": 1.0,
                "risk_multiplier": 1.05,
                "revenue_multiplier": 1.25,
                "msg": "大促季来临：营收增长，但线上稳定性压力变大。",
            },
        ]
        ev = random.choice(events)
        self.state.global_modifiers["kpi_multiplier"] = ev["kpi_multiplier"]
        self.state.global_modifiers["risk_multiplier"] = ev["risk_multiplier"]
        self.state.global_modifiers["revenue_multiplier"] = ev["revenue_multiplier"]

        self.state.chat_history.append({
            "sender": "System",
            "content": ev["msg"],
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })
        self._add_fact(f"第{self.state.week}周：{ev['title']}")

    def _maybe_new_project(self, channel: str):
        if self.state.week % 104 != 0:
            return

        new_id = f"NEW_{self.state.week}"
        if new_id in self.state.projects:
            return

        types = [ProjectType.GAME, ProjectType.APP, ProjectType.INFRA]
        ptype = random.choice(types)
        difficulty = random.randint(2, 5)
        risk = random.randint(10, 35)
        status = ProjectStatus.RD
        name = f"新预研项目 {self.state.week} ({ptype.value})"
        self.state.projects[new_id] = Project(name=name, type=ptype, status=status, difficulty=difficulty, risk=risk)

        self.state.chat_history.append({
            "sender": "System",
            "content": f"{name} 立项了：难度 {difficulty}，风险 {risk}。",
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })
        self._add_fact(f"第{self.state.week}周：立项 {name}")

    async def init_game(self, req: OnboardRequest) -> GameState:
        learning_rate = 1.0
        max_energy = 100
        money = 5000
        
        if req.role == Role.PRODUCT:
            hard, soft = 30, 70
            learning_rate = 1.1 # Product learns soft skills faster maybe? Or just general
        elif req.role == Role.DEV:
            hard, soft = 70, 30
            max_energy = 120 # Devs have more energy to burn
        else:
            hard, soft = 50, 50
            money = 8000
            
        player = Player(
            name=req.name,
            role=req.role,
            hard_skill=hard,
            soft_skill=soft,
            money=money,
            learning_rate=learning_rate,
            max_energy=max_energy,
            energy=max_energy,
            current_project=req.project_name
        )
        
        # 2. Setup State
        self.state.player = player
        self.state.projects = {k: v.model_copy(deep=True) for k, v in INITIAL_PROJECTS.items()}
        self.state.npcs = {k: v.model_copy(deep=True) for k, v in INITIAL_NPCS.items()}
        self.state.chat_history = []
        self.state.week = 1
        self.state.year = 1
        self.state.quarter = 1
        self.state.day_of_week = 1
        self.state.global_modifiers = {
            "kpi_multiplier": 1.0,
            "risk_multiplier": 1.0,
            "revenue_multiplier": 1.0,
        }
        self.state.memory_facts = []
        self.state.memory_summary = ""
        self.state.game_over = False
        self.state.ending = ""
        self.state.known_npcs = []
        self.state.player_subordinates = []
        self._init_npc_relations()
        
        # 3. Add Welcome Message
        self.state.chat_history.append({
            "sender": "System",
            "content": f"欢迎入职米哈游！你现在的身份是 P5 {req.role.value}。你被分配到了 {req.project_name} 项目组。工位已准备就绪。",
            "type": "system",
            "timestamp": self._get_timestamp()
        })
        
        # 4. Determine Project Leader and Direct Manager, then Trigger Welcome Task (via LLM)
        project_leader_id = self._determine_project_leader(req.project_name)
        direct_manager_id = self._determine_direct_manager(req.project_name)

        if project_leader_id or direct_manager_id:
            manager = self.state.npcs.get(direct_manager_id) if direct_manager_id else None
            project_leader = self.state.npcs.get(project_leader_id) if project_leader_id else None
            parts = []
            if manager and project_leader and manager.id == project_leader.id:
                parts.append(f"你的直属上级和 {req.project_name} 项目的负责人都是 {manager.name}（{manager.role}，{manager.level}）。")
            else:
                if manager:
                    parts.append(f"你的直属上级是 {manager.name}（{manager.role}，{manager.level}）。")
                if project_leader:
                    parts.append(f"{req.project_name} 项目的负责人是 {project_leader.name}（{project_leader.role}，{project_leader.level}）。")
            if parts:
                self.state.chat_history.append({
                    "sender": "System",
                    "content": " ".join(parts),
                    "type": "system",
                    "target": "group",
                    "timestamp": self._get_timestamp()
                })

        leader_id = direct_manager_id or project_leader_id
        if leader_id:
            player.leader_id = leader_id
            leader = self.state.npcs[leader_id]
            self._mark_npc_known(leader_id)
            if req.role == Role.PRODUCT:
                task_msg = f"@{req.name} 欢迎加入{req.project_name}。我是{leader.name}。先把PRD文档看一遍，梳理下需求池。"
            elif req.role == Role.OPS:
                task_msg = f"@{req.name} 欢迎加入{req.project_name}。我是{leader.name}。先去社区看看玩家反馈，整理下舆情周报。"
            else:
                task_msg = f"@{req.name} 欢迎加入{req.project_name}。我是{leader.name}。先把环境配好，熟悉下代码库。有不懂的随时问。"
            self.state.chat_history.append({
                "sender": leader.name, 
                "content": task_msg,
                "type": "npc",
                "target": "group",
                "timestamp": self._get_timestamp()
            })
            asyncio.create_task(self._try_generate_welcome(req, leader))
        
        if random.random() < 0.5:
            asyncio.create_task(self._safe_call(asyncio.wait_for(self._trigger_random_event("group"), timeout=3.0)))
        asyncio.create_task(self._safe_call(asyncio.wait_for(self._refresh_suggested_replies("group"), timeout=3.0)))
        
        return self.state

    def _determine_project_leader(self, project: str) -> str:
        candidates = []
        for npc_id, npc in self.state.npcs.items():
            if getattr(npc, "status", "在职") != "在职":
                continue
            if npc.project != project:
                continue
            level_num = self._parse_level(npc.level)
            score = level_num
            if "负责人" in npc.name or "负责人" in npc.role or "负责人" in npc.traits:
                score += 2
            if level_num >= 8:
                score += 1
            candidates.append((score, npc_id))
        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1]
        return None

    def _determine_direct_manager(self, project: str) -> str:
        player = self.state.player
        player_level_num = self._parse_level(player.level) if player else 5
        candidates = []
        for npc_id, npc in self.state.npcs.items():
            if getattr(npc, "status", "在职") != "在职":
                continue
            if npc.project != project:
                continue
            level_num = self._parse_level(npc.level)
            score = 0
            # 更希望是比玩家高 1-2 级的中层
            score -= abs(level_num - (player_level_num + 1))
            # 太高的等级（P9/P10）作为直属上级不太合理，降低权重
            if level_num >= 9:
                score -= 3
            # 明确标记为“负责人”的，更像项目 owner 而非直接主管，略减分
            if "负责人" in npc.name or "负责人" in npc.role or "负责人" in npc.traits:
                score -= 2
            # 至少要不低于玩家等级
            if level_num < player_level_num:
                score -= 2
            candidates.append((score, npc_id))
        if candidates:
            candidates.sort(reverse=True)
            return candidates[0][1]
        return self._determine_project_leader(project)

    async def _infer_relevant_npc_by_text(self, text: str) -> str:
        player = self.state.player
        if not player:
            return None

        topic_res = await llm_service.extract_player_topics(text)
        raw_keywords = topic_res.get("keywords") or []
        keywords = [str(k).strip().lower() for k in raw_keywords if isinstance(k, str) and k.strip()]

        if not keywords:
            base_text = (text or "").strip()
            if not base_text:
                return None
            keywords = [base_text.lower()]

        scored = []
        for nid, npc in self.state.npcs.items():
            status = getattr(npc, "status", "在职")
            if status != "在职":
                continue

            name_str = str(getattr(npc, "name", nid) or "")
            base_name = name_str.split("（")[0].split("(")[0].strip()
            text_blob = " ".join([
                name_str,
                base_name,
                str(getattr(npc, "role", "")),
                str(getattr(npc, "traits", "")),
                str(getattr(npc, "project", "")),
            ]).lower()

            score = 0
            for kw in keywords:
                if not kw:
                    continue
                norm_kw = "".join(ch for ch in kw if not ch.isspace())
                if not norm_kw:
                    continue
                if len(norm_kw) < 2:
                    if norm_kw in text_blob:
                        score += 1
                    continue
                matched = False
                for i in range(len(norm_kw) - 1):
                    sub = norm_kw[i:i+2]
                    if sub and sub in text_blob:
                        score += 2
                        matched = True
                        break
                if not matched and norm_kw in text_blob:
                    score += 2

            if base_name and base_name in text:
                score += 5

            if score > 0:
                scored.append((score, nid))

        if not scored:
            return None

        scored.sort(key=lambda x: x[0], reverse=True)
        player_project = getattr(player, "current_project", None)

        best_id = None
        if player_project:
            for score, nid in scored:
                npc = self.state.npcs.get(nid)
                if not npc:
                    continue
                if getattr(npc, "project", None) == player_project:
                    best_id = nid
                    break

        if not best_id:
            best_id = scored[0][1]

        if best_id:
            self._mark_npc_known(best_id)
            return best_id
        return None

    async def stream_text_action(self, text: str, target_npc: str = None):
        if self.state.active_global_event:
            yield f"data: {json.dumps({'type': 'error', 'content': '当前有全局事件进行中，请先处理事件提示。'})}\n\n"
            return
        if not self.state.player or self.state.game_over:
            yield f"data: {json.dumps({'type': 'error', 'content': 'Game Over'})}\n\n"
            return
            
        player = self.state.player
        channel = target_npc if target_npc else "group"

        if self.state.promotion_review and (self.state.promotion_review.get("status") or "") == "pending_answer":
            player_msg = {
                "sender": "Me",
                "content": text,
                "type": "player",
                "target": channel,
                "timestamp": self._get_timestamp()
            }
            self.state.chat_history.append(player_msg)
            yield f"data: {json.dumps({'type': 'msg_append', 'msg': player_msg})}\n\n"
            prev_len = len(self.state.chat_history)
            await self._handle_promotion_answer(text, channel)
            if len(self.state.chat_history) > prev_len:
                for msg in self.state.chat_history[prev_len:]:
                    yield f"data: {json.dumps({'type': 'msg_append', 'msg': msg})}\n\n"
            self._advance_time(channel, days=1)
            self._check_game_over(channel)
        # 1. Handle Commands (Fast Path)
        if text.startswith("cmd:"):
            self._handle_command(text, channel)
            if random.random() < 0.1:
                player_project = getattr(self.state.player, "current_project", None)
                candidates = [
                    nid for nid, npc in self.state.npcs.items()
                    if getattr(npc, "status", "在职") == "在职"
                    and getattr(npc, "project", None) in [player_project, "General", "HR"]
                ]
            else:
                candidates = []
            if candidates:
                npc_id = random.choice(candidates)
                npc_data = self.state.npcs.get(npc_id)
                if npc_data:
                    recent_history = [
                        {"sender": msg["sender"], "content": msg["content"]}
                        for msg in self.state.chat_history[-5:]
                    ]
                    gen_result = await llm_service.process_action(
                        text,
                        player.dict(),
                        chat_history=recent_history,
                        target_npc=npc_data.dict(),
                    )
                    npc_reply = gen_result.get("npc_reply")
                    if npc_reply:
                        npc_name = gen_result.get("npc_name") or getattr(npc_data, "name", npc_id)
                        msg = {
                            "sender": npc_name,
                            "content": npc_reply,
                            "type": "npc",
                            "target": channel,
                            "timestamp": self._get_timestamp(),
                        }
                        self.state.chat_history.append(msg)
                        yield f"data: {json.dumps({'type': 'msg_append', 'msg': msg})}\n\n"
            self._advance_time(channel, weeks=1, global_event_prob=0.05)
            self._check_game_over(channel)
            yield f"data: {json.dumps({'type': 'state_update', 'state': self.state.dict()})}\n\n"
            return

        # 2. Append Player Message
        player_msg = {
            "sender": "Me",
            "content": text,
            "type": "player",
            "target": channel,
            "timestamp": self._get_timestamp()
        }
        self.state.chat_history.append(player_msg)
        # Yield player message confirmation
        yield f"data: {json.dumps({'type': 'msg_append', 'msg': player_msg})}\n\n"

        inferred_intent, inferred_magnitude = self._infer_intent_magnitude(text)
        inferred_narrative = self._apply_effects(inferred_intent, inferred_magnitude, text, channel=channel)
        applied_intent = True
        if inferred_narrative:
            sys_msg = {
                "sender": "System",
                "content": inferred_narrative,
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            }
            self.state.chat_history.append(sys_msg)
            yield f"data: {json.dumps({'type': 'msg_append', 'msg': sys_msg})}\n\n"

        conflict_npcs = []
        if channel == "group":
            self._context_capture(text)
            prev_len = len(self.state.chat_history)
            conflict_npcs = self._context_event_infer(text, channel)
            if len(self.state.chat_history) > prev_len:
                msg = self.state.chat_history[-1]
                yield f"data: {json.dumps({'type': 'msg_append', 'msg': msg})}\n\n"

        event_mode = False
        if conflict_npcs:
            event_mode = True
        elif channel == "group":
            selected_topic_ids = await self._select_topic_npcs(text, channel)
            if len(selected_topic_ids) >= 2:
                event_mode = True
        
        if not event_mode:
            active_npc_id = target_npc if target_npc != "group" else None
            if not active_npc_id:
                for npc_id, npc_data in self.state.npcs.items():
                    name_str = str(getattr(npc_data, "name", npc_id) or "")
                    base_name = name_str.split("（")[0].split("(")[0].strip()
                    if (
                        f"@{npc_id}" in text
                        or f"@{name_str}" in text
                        or (name_str and name_str in text)
                        or (base_name and base_name in text)
                    ):
                        active_npc_id = npc_id
                        break
            if not active_npc_id:
                active_npc_id = await self._infer_relevant_npc_by_text(text)

            target_npc_data = self.state.npcs.get(active_npc_id, {}) if active_npc_id else {}
            recent_history = [
                {"sender": msg["sender"], "content": msg["content"]}
                for msg in self.state.chat_history[-5:]
            ]

            stream_gen = llm_service.process_action_stream(
                text,
                player.dict(),
                chat_history=recent_history,
                target_npc=target_npc_data.dict() if target_npc_data else None,
            )

            applied_intent = True
            llm_reply_appended = False

            def parse_intent_magnitude(content: str):
                intent = None
                magnitude = 1.0
                for raw in (content or "").splitlines():
                    line = raw.strip()
                    if not line:
                        continue
                    if line.startswith("intent:"):
                        intent = line.split("intent:", 1)[1].strip().upper()
                    elif line.startswith("magnitude:"):
                        try:
                            magnitude = float(line.split("magnitude:", 1)[1].strip())
                        except Exception:
                            magnitude = 1.0
                if not intent:
                    return None, 1.0
                return intent, max(0.0, min(2.0, magnitude))

            def process_content(tag, content):
                content = content.strip()
                if not content:
                    return

                nonlocal applied_intent
                nonlocal llm_reply_appended

                if tag == "analysis":
                    if applied_intent:
                        return None
                    intent, magnitude = parse_intent_magnitude(content)
                    if intent:
                        narrative = self._apply_effects(intent, magnitude, text, channel=channel)
                        applied_intent = True
                        if narrative:
                            msg = {
                                "sender": "System",
                                "content": narrative,
                                "type": "system",
                                "target": channel,
                                "timestamp": self._get_timestamp(),
                            }
                            self.state.chat_history.append(msg)
                            return json.dumps({"type": "msg_append", "msg": msg})
                    return None

                if tag == "narrative":
                    msg = {
                        "sender": "System",
                        "content": content,
                        "type": "system",
                        "target": channel,
                        "timestamp": self._get_timestamp(),
                    }
                    self.state.chat_history.append(msg)
                    return json.dumps({"type": "msg_append", "msg": msg})

                elif tag == "reply":
                    sender = active_npc_id if active_npc_id else "System"
                    msg = {
                        "sender": sender,
                        "content": content,
                        "type": "npc",
                        "target": channel,
                        "timestamp": self._get_timestamp(),
                    }
                    self.state.chat_history.append(msg)
                    llm_reply_appended = True
                    return json.dumps({"type": "msg_append", "msg": msg})

                elif tag == "effects":
                    lines = content.split("\n")
                    for line in lines:
                        if "mood:" in line:
                            val = int(line.split(":")[1].strip())
                            player.mood = max(0, min(100, player.mood + val))
                        if "trust:" in line and active_npc_id:
                            val = int(line.split(":")[1].strip())
                            npc = self.state.npcs[active_npc_id]
                            npc.trust = max(0, min(100, npc.trust + val))
                            if self._is_executive(npc):
                                player.political_capital = max(0, player.political_capital + max(0, int(val / 2)))
                    return json.dumps({"type": "state_update", "state": self.state.dict()})
                return None

            full_response = ""
            processed_pos = 0

            async for chunk in stream_gen:
                full_response += chunk

                import re

                tags = ["analysis", "narrative", "reply", "effects"]
                for tag in tags:
                    close_tag = f"</{tag}>"
                    if close_tag in full_response[processed_pos:]:
                        pattern = f"<{tag}.*?>(.*?)</{tag}>"
                        match = re.search(pattern, full_response, re.DOTALL)
                        if match:
                            content = match.group(1).strip()
                            match_end = match.end()
                            if match_end > processed_pos:
                                res_json = process_content(tag, content)
                                if res_json:
                                    yield f"data: {res_json}\n\n"

                                if tag == "reply":
                                    open_tag_match = re.search(f"<{tag}(.*?)>", full_response)
                                    if open_tag_match:
                                        attrs = open_tag_match.group(1)
                                        if 'npc="' in attrs:
                                            npc_name = attrs.split('npc="')[1].split('"')[0]
                                            self.state.chat_history[-1]["sender"] = npc_name
                                            yield f"data: {json.dumps({'type': 'msg_update', 'msg': self.state.chat_history[-1]})}\n\n"

                                processed_pos = match_end

            if not llm_reply_appended:
                try:
                    fallback_res = await llm_service.process_action(
                        text,
                        player.dict(),
                        chat_history=recent_history,
                        target_npc=target_npc_data.dict() if target_npc_data else None,
                    )
                    if fallback_res:
                        npc_reply = fallback_res.get("npc_reply")
                        if npc_reply:
                            if target_npc_data:
                                default_name = getattr(target_npc_data, "name", active_npc_id if active_npc_id else "System")
                            else:
                                default_name = active_npc_id if active_npc_id else "System"
                            npc_name = fallback_res.get("npc_name") or default_name
                            msg = {
                                "sender": npc_name,
                                "content": npc_reply,
                                "type": "npc",
                                "target": channel,
                                "timestamp": self._get_timestamp(),
                            }
                            self.state.chat_history.append(msg)
                            yield f"data: {json.dumps({'type': 'msg_append', 'msg': msg})}\n\n"
                        sys_narrative = fallback_res.get("system_narrative")
                        if sys_narrative:
                            sys_msg = {
                                "sender": "System",
                                "content": sys_narrative,
                                "type": "system",
                                "target": channel,
                                "timestamp": self._get_timestamp(),
                            }
                            self.state.chat_history.append(sys_msg)
                            yield f"data: {json.dumps({'type': 'msg_append', 'msg': sys_msg})}\n\n"
                except Exception:
                    pass

        if channel == "group" and len(self.state.npcs) > 1:
            prev_len = len(self.state.chat_history)
            responders = conflict_npcs if conflict_npcs else []
            await self._npc_cross_talk(text, responders, channel)
            if len(self.state.chat_history) > prev_len:
                for msg in self.state.chat_history[prev_len:]:
                    yield f"data: {json.dumps({'type': 'msg_append', 'msg': msg})}\n\n"

        # 6. Check Random Events (Async)
        if random.random() < 0.1:
            prev_len = len(self.state.chat_history)
            await self._trigger_random_event(channel)
            if len(self.state.chat_history) > prev_len:
                new_msg = self.state.chat_history[-1]
                yield f"data: {json.dumps({'type': 'msg_append', 'msg': new_msg})}\n\n"

        self._advance_time(channel, days=1)
        self._check_game_over(channel)
        try:
            await asyncio.wait_for(self._refresh_suggested_replies(channel), timeout=5.0)
        except Exception:
            pass
        yield f"data: {json.dumps({'type': 'state_update', 'state': self.state.dict()})}\n\n"
        yield "data: [DONE]\n\n"

    async def process_text_action(self, text: str, target_npc: str = None) -> GameState:
        if self.state.active_global_event:
            return self.state
        if not self.state.player or self.state.game_over:
            return self.state
            
        player = self.state.player
        narrative = ""
        channel = target_npc if target_npc else "group"

        if self.state.promotion_review and (self.state.promotion_review.get("status") or "") == "pending_answer":
            player_msg = {
                "sender": "Me",
                "content": text,
                "type": "player",
                "target": channel,
                "timestamp": self._get_timestamp()
            }
            self.state.chat_history.append(player_msg)
            await self._handle_promotion_answer(text, channel)
            self._advance_time(channel, days=1)
            self._check_game_over(channel)
            try:
                await self._refresh_suggested_replies(channel)
            except Exception:
                pass
            return self.state

        # 1. Handle Workbench Actions (Commands)
        if text.startswith("cmd:"):
            self._handle_command(text, channel)
            if channel != "workbench":
                if random.random() < 0.1:
                    player_project = getattr(player, "current_project", None)
                    candidates = [
                        nid for nid, npc in self.state.npcs.items()
                        if getattr(npc, "status", "在职") == "在职"
                        and getattr(npc, "project", None) in [player_project, "General", "HR"]
                    ]
                else:
                    candidates = []
                if candidates:
                    npc_id = random.choice(candidates)
                    npc_data = self.state.npcs.get(npc_id)
                    if npc_data:
                        recent_history = [
                            {"sender": msg["sender"], "content": msg["content"]}
                            for msg in self.state.chat_history[-5:]
                        ]
                        gen_result = await llm_service.process_action(
                            text,
                            player.dict(),
                            chat_history=recent_history,
                            target_npc=npc_data.dict(),
                        )
                        npc_reply = gen_result.get("npc_reply")
                        if npc_reply:
                            npc_name = gen_result.get("npc_name") or getattr(npc_data, "name", npc_id)
                            self.state.chat_history.append({
                                "sender": npc_name,
                                "content": npc_reply,
                                "type": "npc",
                                "target": channel,
                                "timestamp": self._get_timestamp()
                            })
                self._advance_time(channel, days=1, global_event_prob=0.05)
                self._check_game_over(channel)
            return self.state

        # 2. Process Action via LLM (Combined Analysis + Generation)
        # We skip separate analysis step to speed up
        
        # 4. Handle Mentions in Group Chat
        active_npc_id = target_npc if target_npc != "group" else None
        if not active_npc_id:
            for npc_id, npc_data in self.state.npcs.items():
                if f"@{npc_id}" in text or f"@{npc_data.name}" in text or npc_data.name in text:
                    active_npc_id = npc_id
                    break

        # Append Player Message EARLY so it appears in history for NPCs
        self.state.chat_history.append({
            "sender": "Me",
            "content": text,
            "type": "player",
            "target": channel,
            "timestamp": self._get_timestamp()
        })
        
        conflict_npcs = []
        if channel == "group":
            self._context_capture(text)
            conflict_npcs = self._context_event_infer(text, channel)

        inferred_intent, inferred_magnitude = self._infer_intent_magnitude(text)
        narrative = self._apply_effects(inferred_intent, inferred_magnitude, text, channel=channel)

        # 5. Determine Responders (Multi-NPC Logic)
        responders = []
        if conflict_npcs:
            responders = conflict_npcs
        elif active_npc_id:
            responders.append(active_npc_id)
        elif channel == "group" and random.random() < 0.7:
            candidates = [
                nid for nid, npc in self.state.npcs.items() 
                if npc.project in [player.current_project, "General", "HR"]
            ]
            if candidates:
                num_responders = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
                responders = random.sample(candidates, min(len(candidates), num_responders))

        if responders:
            async def run_for_npc(npc_id: str):
                active_npc_data = self.state.npcs.get(npc_id, {})
                recent_history = [
                    {"sender": msg["sender"], "content": msg["content"]}
                    for msg in self.state.chat_history[-5:]
                ]
                gen_result = await llm_service.process_action(
                    text,
                    player.dict(),
                    chat_history=recent_history,
                    target_npc=active_npc_data.dict(),
                )
                return npc_id, gen_result

            tasks = [run_for_npc(nid) for nid in responders]
            results = await asyncio.gather(*tasks)

            for npc_id, gen_result in results:
                if not gen_result:
                    continue

                if "mood_change" in gen_result:
                    player.mood = max(0, min(100, player.mood + gen_result["mood_change"]))

                if "trust_change" in gen_result:
                    npc = self.state.npcs[npc_id]
                    npc.trust = max(0, min(100, npc.trust + gen_result["trust_change"]))
                    if gen_result["trust_change"] < 0:
                        narrative += f" {npc.name} 对你的信任度下降了。"

                if gen_result.get("npc_reply"):
                    active_npc_data = self.state.npcs.get(npc_id, {})
                    if hasattr(active_npc_data, "name"):
                        default_name = active_npc_data.name
                    else:
                        default_name = npc_id
                    npc_name = gen_result.get("npc_name", default_name)
                    self.state.chat_history.append({
                        "sender": npc_name,
                        "content": gen_result["npc_reply"],
                        "type": "npc",
                        "target": channel,
                        "timestamp": self._get_timestamp()
                    })

                sys_narrative = gen_result.get("system_narrative")
                if sys_narrative:
                    sys_text = str(sys_narrative).strip()
                    if not sys_text.startswith("你在群里随便唠了两句"):
                        self.state.chat_history.append({
                            "sender": "System",
                            "content": sys_text,
                            "type": "system",
                            "target": channel,
                            "timestamp": self._get_timestamp()
                        })

        if channel == "group" and len(self.state.npcs) > 1:
            await self._npc_cross_talk(text, responders, channel)

        if narrative:
            self.state.chat_history.append({
                "sender": "System",
                "content": narrative,
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            })

        if random.random() < 0.03:
            await self._trigger_random_event(channel)
        
        self._advance_time(channel, days=1)
        self._check_game_over(channel)
        try:
            await self._refresh_suggested_replies(channel)
        except Exception:
            pass
        return self.state
    
    async def _handle_promotion_answer(self, text: str, channel: str):
        player = self.state.player
        if not player:
            return
        review = self.state.promotion_review or {}
        if not review:
            return
        status = review.get("status") or ""
        if status != "pending_answer":
            return
        answer = (text or "").strip()
        if not answer:
            return
        review["answer"] = answer
        review["status"] = "pending_score"
        self.state.promotion_review = review
        score_result = await llm_service.score_promotion_answer(
            {
                "role": getattr(player, "role", None),
                "level": getattr(player, "level", None),
                "current_project": getattr(player, "current_project", None),
            },
            {
                "target_level": f"P{review.get('target_level')}",
                "question": review.get("question"),
                "answer": answer,
            },
        )
        score = int(score_result.get("score", 0))
        comment = str(score_result.get("comment", "")).strip()
        threshold = int(review.get("score_threshold") or 60)
        passed = score >= threshold
        review["score"] = score
        review["comment"] = comment
        review["passed"] = passed
        review["status"] = "finished"
        self.state.promotion_review = review
        msg1 = f"本次述职得分：{score} 分（通过线 {threshold} 分）。"
        self.state.chat_history.append({
            "sender": "System",
            "content": msg1,
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })
        if comment:
            self.state.chat_history.append({
                "sender": "System",
                "content": f"{comment}",
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            })
        if passed:
            target_level = review.get("target_level")
            current_num = self._parse_level(player.level)
            if isinstance(target_level, int) and target_level > current_num:
                player.level = f"P{target_level}"
                self._add_fact(f"晋升 {player.level}")
            msg2 = f"恭喜！通过述职评审，你晋升为 {player.level}。"
        else:
            msg2 = "本轮述职未达到通过标准，可以在后续评估周期继续冲刺。"
        self.state.chat_history.append({
            "sender": "System",
            "content": msg2,
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })
    
    def _context_capture(self, text: str):
        key = ""
        t = text or ""
        if "邀请制" in t:
            key = "邀请制"
        if not key:
            return
        slots = self.state.context_slots.get(key) or {}
        prod_id = slots.get("Product")
        dev_id = slots.get("Dev")
        if not prod_id or not dev_id:
            for nid, npc in self.state.npcs.items():
                name = getattr(npc, "name", "")
                traits = getattr(npc, "traits", "")
                role = getattr(npc, "role", "")
                if not prod_id and role == "Product" and ("邀请制" in traits or "IAM" in traits or getattr(npc, "project", "") == "IAM"):
                    prod_id = nid
                if not dev_id and role == "Dev" and ("邀请制" in traits or "IAM" in traits or getattr(npc, "project", "") == "IAM"):
                    dev_id = nid
        if not prod_id or not dev_id:
            if "NPC_0012" in self.state.npcs and not prod_id:
                prod_id = "NPC_0012"
            if "NPC_0011" in self.state.npcs and not dev_id:
                dev_id = "NPC_0011"
        m = {}
        if prod_id:
            m["Product"] = prod_id
        if dev_id:
            m["Dev"] = dev_id
        if m:
            self.state.context_slots[key] = {**slots, **m}
            self.state.last_topic = key
            if ("谁" in t or "是谁" in t or "who" in t.lower()) and ("产品" in t and ("研发" in t or "工程师" in t)):
                p = self.state.npcs.get(prod_id)
                d = self.state.npcs.get(dev_id)
                if p and d:
                    msg = f"{key} 的产品与研发分别是 {p.name} 与 {d.name}。"
                    self.state.chat_history.append({
                        "sender": "System",
                        "content": msg,
                        "type": "system",
                        "target": "group",
                        "timestamp": self._get_timestamp()
                    })
    
    def _context_event_infer(self, text: str, channel: str) -> list:
        t = text or ""
        topic = ""
        if "邀请制" in t:
            topic = "邀请制"
        if not topic:
            topic = self.state.last_topic or ""
        if not topic:
            return []
        if ("打起来" in t or "吵起来" in t or "冲突" in t) and ("产品" in t and ("研发" in t or "工程师" in t)):
            slots = self.state.context_slots.get(topic) or {}
            prod_id = slots.get("Product")
            dev_id = slots.get("Dev")
            if prod_id and dev_id:
                prod = self.state.npcs.get(prod_id)
                dev = self.state.npcs.get(dev_id)
                if prod and dev:
                    proj_name = prod.project or dev.project or "General"
                    self._emit_relation_conflict(dev, prod, proj_name, channel)
                    return [dev_id, prod_id]
        return []
    
    def _emit_relation_conflict(self, npc_a, npc_b, project_name: str, channel: str):
        player = self.state.player
        npc_a.mood = max(0, npc_a.mood - 4)
        npc_b.mood = max(0, npc_b.mood - 4)
        if player and (project_name == player.current_project):
            player.mood = max(0, player.mood - 2)
        self._mark_npc_known(npc_a.id)
        self._mark_npc_known(npc_b.id)
        msg = f"{npc_a.name} 与 {npc_b.name} 在 {project_name} 项目上发生冲突，群里气氛瞬间凝固。"
        self.state.chat_history.append({
            "sender": "System",
            "content": msg,
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })
    
    def _apply_rice_item(self, item_id: str) -> str:
        player = self.state.player
        if not player:
            return ""
        cfg_map = {item["id"]: item for item in RICE_ITEMS}
        item = cfg_map.get(item_id or "standard") or cfg_map.get("standard")
        if not item:
            return ""
        level_num = self._parse_level(getattr(player, "level", "P5"))
        min_level = self._parse_level(item.get("min_level", "P5"))
        if level_num < min_level:
            return f"当前职级不足，{item['name']} 需要达到 {item.get('min_level', 'P5')} 后解锁。"
        purchases = getattr(player, "workbench_purchases", None)
        if purchases is None:
            purchases = {}
            player.workbench_purchases = purchases
        limit = item.get("limit")
        key = f"rice:{item['id']}"
        if isinstance(limit, int) and limit > 0:
            count = purchases.get(key, 0)
            if count >= limit:
                return f"{item['name']} 为限购商品，本局已无法再次购买。"
        cost = item.get("cost", 0)
        if cost and player.money < cost:
            return "余额不足，无法完成本次消费。"
        if cost:
            player.money -= cost
        energy_gain = item.get("energy", 0)
        mood_gain = item.get("mood", 0)
        if energy_gain:
            player.energy = min(player.max_energy, player.energy + energy_gain)
        if mood_gain:
            player.mood = max(0, min(100, player.mood + mood_gain))
        learning_rate_delta = float(item.get("learning_rate_delta", 0.0) or 0.0)
        learning_rate_chance = float(item.get("learning_rate_chance", 0.0) or 0.0)
        lr_up = False
        if learning_rate_delta and random.random() <= learning_rate_chance:
            player.learning_rate = round(player.learning_rate + learning_rate_delta, 2)
            lr_up = True
        if isinstance(limit, int) and limit > 0:
            purchases[key] = purchases.get(key, 0) + 1
        parts = []
        if energy_gain:
            parts.append(f"精力 +{energy_gain}")
        if mood_gain:
            if mood_gain > 0:
                parts.append(f"心情 +{mood_gain}")
            elif mood_gain < 0:
                parts.append(f"心情 {mood_gain}")
        if cost:
            parts.append(f"金钱 -{cost}")
        if lr_up:
            parts.append(f"悟性倍率 +{learning_rate_delta:.1f}x")
        effect_str = "，".join(parts) if parts else "状态略有变化。"
        base_desc = item.get("desc") or f"你选择了 {item['name']}。"
        if parts:
            return f"{base_desc}{' ' if not base_desc.endswith('。') else ''}{effect_str}。"
        return base_desc
    
    def _apply_shop_item(self, item_id: str, channel: str) -> str:
        player = self.state.player
        if not player:
            return ""
        cfg_map = {item["id"]: item for item in SHOP_ITEMS}
        item = cfg_map.get(item_id or "gift") or cfg_map.get("gift")
        if not item:
            return ""
        level_num = self._parse_level(getattr(player, "level", "P5"))
        min_level = self._parse_level(item.get("min_level", "P5"))
        if level_num < min_level:
            return f"当前职级不足，{item['name']} 需要达到 {item.get('min_level', 'P5')} 后解锁。"
        purchases = getattr(player, "workbench_purchases", None)
        if purchases is None:
            purchases = {}
            player.workbench_purchases = purchases
        limit = item.get("limit")
        key = f"shop:{item['id']}"
        if isinstance(limit, int) and limit > 0:
            count = purchases.get(key, 0)
            if count >= limit:
                return f"{item['name']} 为限购商品，本局已无法再次购买。"
        cost = item.get("cost", 0)
        if cost and player.money < cost:
            return "余额不足，买不起..."
        if item["id"] == "gift":
            player.money -= cost
            candidates = [
                npc for npc in self.state.npcs.values()
                if npc.project in [player.current_project, "General", "HR"]
            ]
            target = None
            if channel and channel != "group" and channel in self.state.npcs:
                target = self.state.npcs[channel]
            elif candidates:
                target = random.choice(candidates)
            if target:
                trust_gain = max(5, min(15, int(5 + player.soft_skill / 20)))
                if channel and channel != "group" and channel == target.id:
                    trust_gain = min(18, int(trust_gain * 1.2))
                target.trust = max(0, min(100, target.trust + trust_gain))
                if self._is_executive(target):
                    player.political_capital = max(0, player.political_capital + max(1, int(math.ceil(trust_gain / 3))))
                purchases[key] = purchases.get(key, 0) + 1
                return f"你在米购买了限量手办送给 {target.name}。Money -{cost}, Trust +{trust_gain}"
            purchases[key] = purchases.get(key, 0) + 1
            return f"你在米购购买了限量手办。Money -{cost}"
        if cost:
            player.money -= cost
        if item["id"] == "gpu":
            player.gear_gpu_level += 1
            player.hard_skill += 3
            return "你在商城购买了一块新显卡。硬技能 +3，显卡等级 +1，金钱 -3000。"
        if item["id"] == "monitor":
            player.gear_monitor_level += 1
            player.mood = max(0, min(100, player.mood + 5))
            return "你换上了新的高刷显示器。Mood +5, 显示器等级 +1, Money -2000"
        if item["id"] == "chair":
            player.gear_chair_level += 1
            player.max_energy += 10
            player.energy = min(player.max_energy, player.energy + 10)
            return "你入手了一把人体工学椅。Max Energy +10, Energy +10, 椅子等级 +1, Money -1500"
        energy_gain = item.get("energy", 0)
        mood_gain = item.get("mood", 0)
        hard_gain = item.get("hard_skill", 0)
        soft_gain = item.get("soft_skill", 0)
        political_gain = item.get("political_capital", 0)
        if energy_gain:
            player.energy = min(player.max_energy, player.energy + energy_gain)
        if mood_gain:
            player.mood = max(0, min(100, player.mood + mood_gain))
        if hard_gain:
            player.hard_skill += hard_gain
        if soft_gain:
            player.soft_skill += soft_gain
        if political_gain:
            player.political_capital = max(0, player.political_capital + political_gain)
        learning_rate_delta = float(item.get("learning_rate_delta", 0.0) or 0.0)
        learning_rate_chance = float(item.get("learning_rate_chance", 0.0) or 0.0)
        lr_up = False
        if learning_rate_delta and random.random() <= learning_rate_chance:
            player.learning_rate = round(player.learning_rate + learning_rate_delta, 2)
            lr_up = True
        if isinstance(limit, int) and limit > 0:
            purchases[key] = purchases.get(key, 0) + 1
        parts = []
        if hard_gain:
            parts.append(f"硬技能 +{hard_gain}")
        if soft_gain:
            parts.append(f"软技能 +{soft_gain}")
        if energy_gain:
            parts.append(f"精力 +{energy_gain}")
        if mood_gain:
            parts.append(f"心情 +{mood_gain}")
        if political_gain:
            parts.append(f"政治资本 +{political_gain}")
        if cost:
            parts.append(f"金钱 -{cost}")
        if lr_up:
            parts.append(f"悟性倍率 +{learning_rate_delta:.1f}x")
        effect_str = "，".join(parts) if parts else "状态略有变化。"
        base_desc = item.get("desc") or f"你在米购购买了 {item['name']}。"
        if parts:
            return f"{base_desc}{' ' if not base_desc.endswith('。') else ''}{effect_str}。"
        return base_desc
    
    def _apply_academy_course(self, course_id: str, channel: str) -> str:
        player = self.state.player
        if not player:
            return ""
        cfg_map = {c["id"]: c for c in ACADEMY_COURSES}
        course = cfg_map.get(course_id or "base") or cfg_map.get("base")
        if not course:
            return ""
        level_num = self._parse_level(getattr(player, "level", "P5"))
        min_level = self._parse_level(course.get("min_level", "P5"))
        if level_num < min_level:
            return f"当前职级不足，{course['name']} 需要达到 {course.get('min_level', 'P5')} 后解锁。"
        purchases = getattr(player, "workbench_purchases", None)
        if purchases is None:
            purchases = {}
            player.workbench_purchases = purchases
        limit = course.get("limit")
        key = f"academy:{course['id']}"
        if isinstance(limit, int) and limit > 0:
            count = purchases.get(key, 0)
            if count >= limit:
                return f"{course['name']} 为限购课程，本局已无法再次报名。"
        cost = course.get("cost", 0)
        energy_cost = course.get("energy_cost", 0)
        if player.money < cost or player.energy < energy_cost:
            return f"资源不足(需要 ¥{cost} + {energy_cost} 精力)，无法报名课程。"
        player.money -= cost
        player.energy -= energy_cost
        hard_gain = course.get("hard_skill", 0)
        soft_gain = course.get("soft_skill", 0)
        if hard_gain:
            player.hard_skill += hard_gain
        if soft_gain:
            player.soft_skill += soft_gain
        learning_rate_delta = float(course.get("learning_rate_delta", 0.0) or 0.0)
        learning_rate_chance = float(course.get("learning_rate_chance", 0.0) or 0.0)
        lr_up = False
        if learning_rate_delta and random.random() <= learning_rate_chance:
            player.learning_rate = round(player.learning_rate + learning_rate_delta, 2)
            lr_up = True
        if isinstance(limit, int) and limit > 0:
            purchases[key] = purchases.get(key, 0) + 1
        parts = []
        if hard_gain:
            parts.append(f"硬技能 +{hard_gain}")
        if soft_gain:
            parts.append(f"软技能 +{soft_gain}")
        if lr_up:
            parts.append(f"悟性倍率 +{learning_rate_delta:.1f}x")
        if energy_cost:
            parts.append(f"精力 -{energy_cost}")
        if cost:
            parts.append(f"金钱 -{cost}")
        effect_str = "，".join(parts) if parts else "状态略有变化。"
        base_desc = course.get("desc") or "你在米忽悠学院上了一节课。"
        if parts:
            return f"{base_desc}{' ' if not base_desc.endswith('。') else ''}{effect_str}。"
        return base_desc
    
    def _handle_command(self, text: str, channel: str) -> GameState:
        player = self.state.player
        raw = text[len("cmd:"):] if text.startswith("cmd:") else text
        parts = raw.split(":")
        cmd = parts[0] if parts else raw
        arg = parts[1] if len(parts) > 1 else None
        narrative = ""
        if not player:
            return self.state
        
        if cmd == "eat_mifan":
            narrative = self._apply_rice_item("standard")
        elif cmd == "eat_mifan_light":
            narrative = self._apply_rice_item("light")
        elif cmd == "eat_mifan_luxury":
            narrative = self._apply_rice_item("luxury")
        elif cmd == "rice":
            narrative = self._apply_rice_item(arg)
        elif cmd == "work_hard":
            narrative = self._apply_effects("WORK", 1.5, "", channel=channel)
        elif cmd == "work_normal":
            base = self._apply_effects("WORK", 1.0, "老实干活推进项目", channel=channel)
            project = self.state.projects.get(player.current_project)
            extra = ""
            if project:
                bonus_max = max(0, int(player.hard_skill / 40))
                prog_bonus = random.randint(0, bonus_max) if bonus_max > 0 else 0
                risk_shift = 0
                if player.mood >= 70:
                    risk_shift = -random.randint(0, 2)
                elif player.mood <= 40:
                    risk_shift = random.randint(0, 2)
                if prog_bonus:
                    project.progress = max(0, min(100, project.progress + prog_bonus))
                    extra += f" 项目额外进度 +{prog_bonus}"
                if risk_shift:
                    project.risk = max(0, min(100, project.risk + risk_shift))
                    if risk_shift < 0:
                        extra += f"，项目风险 {risk_shift}"
                    else:
                        extra += f"，项目风险 +{risk_shift}"
            narrative = base + extra if base else extra
        elif cmd == "tech_breakthrough":
            base = self._apply_effects("WORK", 1.5, "技术突破，加班钻研技术方案", channel=channel)
            project = self.state.projects.get(player.current_project)
            extra_parts = []
            hard_gain_max = 1 + (1 if player.hard_skill >= 60 else 0)
            hard_gain = random.randint(1, hard_gain_max)
            player.hard_skill += hard_gain
            extra_parts.append(f"硬技能 +{hard_gain}")
            if project:
                base_prog = random.randint(2, 5)
                prog_factor = max(0.7, min(1.6, player.hard_skill / 60.0))
                prog_boost = max(1, int(base_prog * prog_factor))
                base_risk = random.randint(1, 3)
                risk_factor = max(0.7, min(1.5, player.hard_skill / 70.0))
                risk_drop = max(1, int(base_risk * risk_factor))
                project.progress = max(0, min(100, project.progress + prog_boost))
                project.risk = max(0, min(100, project.risk - risk_drop))
                extra_parts.append(f"项目进度 +{prog_boost}")
                extra_parts.append(f"项目风险 -{risk_drop}")
            narrative = base or ""
            if extra_parts:
                narrative = f"{narrative} " if narrative else ""
                narrative += "，".join(extra_parts)
        elif cmd == "make_ppt":
            project = self.state.projects.get(player.current_project)
            energy_cost = random.randint(6, 10)
            mood_drop = random.randint(1, 4)
            player.energy = max(0, player.energy - energy_cost)
            player.mood = max(0, min(100, player.mood - mood_drop))
            soft_max = 1 + (1 if player.soft_skill >= 60 else 0)
            soft_gain = random.randint(1, soft_max)
            player.soft_skill += soft_gain
            proj_desc = ""
            if project:
                prog_base = random.randint(0, 2)
                trust_base = random.randint(2, 4)
                morale_base = random.randint(0, 2)
                if player.soft_skill >= 70:
                    trust_base += 1
                prog_gain = prog_base
                trust_gain = trust_base
                morale_gain = morale_base
                project.progress = max(0, min(100, project.progress + prog_gain))
                project.stakeholder_trust = min(100, project.stakeholder_trust + trust_gain)
                project.morale = max(0, min(100, project.morale + morale_gain))
                proj_desc = f"，项目信任 +{trust_gain}，项目进度 +{prog_gain}"
            narrative = f"你花时间包装PPT，为项目讲故事。精力 -{energy_cost}，心情 -{mood_drop}，软技能 +{soft_gain}{proj_desc}。"
        elif cmd == "align_meeting":
            text = "拉群对齐项目节奏"
            base = self._apply_effects("SOCIAL", 1.1, text, channel=channel)
            project = self.state.projects.get(player.current_project)
            extra = ""
            if project:
                prog_base = random.randint(0, 2)
                risk_base = random.randint(0, 2)
                if player.soft_skill >= 60:
                    prog_base += 1
                if player.soft_skill >= 70:
                    risk_base += 1
                prog_gain = max(1, prog_base)
                risk_drop = max(0, risk_base)
                if prog_gain:
                    project.progress = max(0, min(100, project.progress + prog_gain))
                if risk_drop:
                    project.risk = max(0, min(100, project.risk - risk_drop))
                if prog_gain or risk_drop:
                    extra = f" 项目进度 +{prog_gain}，项目风险 -{risk_drop}。"
            narrative = base + extra if base else (extra or "你拉了一场对齐会。")
        elif cmd == "paid_slack":
            project = self.state.projects.get(player.current_project)
            mood_min, mood_max = 2, 6
            if player.mood <= 40:
                mood_max += 2
            mood_gain = random.randint(mood_min, mood_max)
            energy_min, energy_max = 2, 5
            if player.energy <= int(player.max_energy * 0.5):
                energy_max += 1
            energy_gain = random.randint(energy_min, energy_max)
            player.mood = max(0, min(100, player.mood + mood_gain))
            player.energy = min(player.max_energy, player.energy + energy_gain)
            if project:
                prog_loss = random.randint(1, 3)
                if player.hard_skill >= 70 or player.soft_skill >= 70:
                    prog_loss = max(1, prog_loss - 1)
                trust_loss = random.randint(1, 2)
                if player.political_capital >= 10:
                    trust_loss = max(1, trust_loss - 1)
                project.progress = max(0, min(100, project.progress - prog_loss))
                project.stakeholder_trust = max(0, project.stakeholder_trust - trust_loss)
                narrative = f"你选择在工位带薪摸鱼，心情 +{mood_gain}，精力 +{energy_gain}，项目进度 -{prog_loss}，项目信任 -{trust_loss}。"
            else:
                narrative = f"你选择在工位带薪摸鱼，心情 +{mood_gain}，精力 +{energy_gain}。"
        elif cmd == "rest":
            narrative = self._apply_effects("REFUSE", 1.0, "", channel=channel)
        elif cmd == "report":
            narrative = self._apply_effects("WORK", 1.0, "", channel=channel)
        elif cmd == "msg_boss":
            narrative = self._apply_manage_up(channel)
        elif cmd == "buy_gift":
            narrative = self._apply_shop_item("gift", channel)
        elif cmd == "buy_gpu":
            narrative = self._apply_shop_item("gpu", channel)
        elif cmd == "buy_monitor":
            narrative = self._apply_shop_item("monitor", channel)
        elif cmd == "buy_chair":
            narrative = self._apply_shop_item("chair", channel)
        elif cmd == "shop":
            narrative = self._apply_shop_item(arg, channel)
        elif cmd == "learn_skill":
            narrative = self._apply_academy_course("base", channel)
        elif cmd == "train_hard":
            narrative = self._apply_academy_course("hard_camp", channel)
        elif cmd == "train_soft":
            narrative = self._apply_academy_course("soft_workshop", channel)
        elif cmd == "train_leadership":
            narrative = self._apply_academy_course("leadership", channel)
        elif cmd == "academy":
            narrative = self._apply_academy_course(arg, channel)
        elif cmd == "transfer":
            target_project = (arg or "").strip()
            if not target_project:
                narrative = "转岗失败：缺少目标项目（例如 cmd:transfer:HSR）。"
            else:
                proj = self.state.projects.get(target_project)
                if not proj:
                    narrative = f"转岗失败：未找到项目 {target_project}。"
                elif proj.status == ProjectStatus.CANCELED:
                    narrative = f"转岗失败：{proj.name} 已被砍。"
                else:
                    player.current_project = target_project
                    narrative = f"你提交了转岗申请，已加入 {proj.name}。"
                    self._add_fact(f"转岗 {proj.name}")
        elif cmd == "add_subordinate":
            npc_id = (arg or "").strip()
            if self._parse_level(player.level) < 7:
                narrative = "权限不足：需晋升至 P7 及以上才能管理下属。"
            elif not npc_id or npc_id not in self.state.npcs:
                narrative = "添加下属失败：未找到该 NPC。"
            else:
                npc = self.state.npcs[npc_id]
                if npc.status != "在职":
                    narrative = f"添加下属失败：{npc.name} 当前不在职。"
                elif npc_id in self.state.player_subordinates:
                    narrative = f"{npc.name} 已经是你的下属了。"
                elif npc.project not in [player.current_project, "General", "HR"]:
                    narrative = f"添加下属失败：{npc.name} 不在你当前项目线，无法直接管理。"
                elif self._parse_level(npc.level) >= self._parse_level(player.level):
                    narrative = f"添加下属失败：{npc.name} 职级不低于你。"
                else:
                    self.state.player_subordinates.append(npc_id)
                    npc.manager_id = player.name
                    narrative = f"你正式将 {npc.name} 划入麾下，成为你的下属。"
        elif cmd == "remove_subordinate":
            npc_id = (arg or "").strip()
            if npc_id in self.state.player_subordinates:
                self.state.player_subordinates = [
                    sid for sid in self.state.player_subordinates if sid != npc_id
                ]
                npc = self.state.npcs.get(npc_id)
                if npc and getattr(npc, "manager_id", None) == player.name:
                    npc.manager_id = None
                narrative = f"你与 {npc.name if npc else npc_id} 解除了一对一汇报关系。"
            else:
                narrative = "当前没有该下属记录。"
        elif cmd == "sub_work":
            npc_id = (arg or "").strip()
            if self._parse_level(player.level) < 7:
                narrative = "指派失败：需晋升至 P7 及以上才能指派下属工作。"
            elif not npc_id or npc_id not in self.state.npcs:
                narrative = "指派失败：未找到该 NPC。"
            elif npc_id not in self.state.player_subordinates:
                narrative = "指派失败：该 NPC 不是你的下属。"
            else:
                npc = self.state.npcs[npc_id]
                project = self.state.projects.get(player.current_project)
                if not project:
                    narrative = "指派失败：当前无有效项目。"
                else:
                    fatigue = random.randint(5, 15)
                    mood_delta = -random.randint(0, 8)
                    npc.mood = max(0, min(100, npc.mood + mood_delta))
                    efficiency = max(1, int(self._parse_level(npc.level) / 2))
                    prog_gain = max(1, efficiency)
                    project.progress = min(200, project.progress + prog_gain)
                    trust_delta = -2 if npc.mood < 40 else 1
                    npc.trust = max(0, min(100, npc.trust + trust_delta))
                    if trust_delta < 0:
                        narrative = f"{npc.name} 帮你推进了一些工作，但对频繁加班有点不满。项目进度 +{prog_gain}。"
                    else:
                        narrative = f"{npc.name} 主动加班帮你推进项目。项目进度 +{prog_gain}。"
        elif cmd == "sub_all_work":
            if self._parse_level(player.level) < 7:
                narrative = "指派失败：需晋升至 P7 及以上才能指派下属工作。"
            elif not self.state.player_subordinates:
                narrative = "你目前还没有任何下属可以指派。"
            else:
                project = self.state.projects.get(player.current_project)
                if not project:
                    narrative = "指派失败：当前无有效项目。"
                else:
                    total_progress = 0
                    unhappy = 0
                    for npc_id in list(self.state.player_subordinates):
                        npc = self.state.npcs.get(npc_id)
                        if not npc or npc.status != "在职":
                            continue
                        efficiency = max(1, int(self._parse_level(npc.level) / 2))
                        total_progress += efficiency
                        npc.mood = max(0, min(100, npc.mood - random.randint(3, 10)))
                        if npc.mood < 35:
                            unhappy += 1
                            npc.trust = max(0, npc.trust - 3)
                    if total_progress > 0:
                        project.progress = min(200, project.progress + total_progress)
                        narrative = f"你发动下属集体推进项目，项目进度 +{total_progress}。"
                        if unhappy > 0:
                            narrative += f" 不过有 {unhappy} 位下属对高强度压榨颇有怨言。"
                    else:
                        narrative = "下属们今天都抽不出手来帮你干活。"
        elif cmd == "resign":
            self.state.game_over = True
            self.state.ending = "Resignation"
            narrative = "你提交了离职申请。再见了，工位与周报。"
        
        if narrative:
            if channel == "workbench":
                source = "workbench"
                if cmd in ["rice", "eat_mifan", "eat_mifan_light", "eat_mifan_luxury"]:
                    source = "rice"
                elif cmd in ["shop", "buy_gift", "buy_gpu", "buy_monitor", "buy_chair"]:
                    source = "shop"
                elif cmd in ["academy", "learn_skill", "train_hard", "train_soft", "train_leadership"]:
                    source = "academy"
                self.state.workbench_feedback.append({
                    "source": source,
                    "content": narrative,
                    "timestamp": self._get_timestamp()
                })
            else:
                self.state.chat_history.append({
                    "sender": "System",
                    "content": narrative,
                    "type": "system",
                    "target": channel,
                    "timestamp": self._get_timestamp()
                })
        return self.state

    def _apply_manage_up(self, channel: str) -> str:
        player = self.state.player
        if not player:
            return ""
        # 消耗精力
        player.energy = max(0, player.energy - 8)
        exec_ids = self._get_top_executives_ids()
        target_id = None
        # Prefer current project's leader if they are executive
        leader_id = self._determine_project_leader(player.current_project) if player.current_project else None
        leader = self.state.npcs.get(leader_id) if leader_id else None
        if leader and self._is_executive(leader):
            target_id = leader_id
        elif exec_ids:
            target_id = exec_ids[0]
        if not target_id:
            return "你尝试向上管理，但当前没有明确的大佬可以沟通。"
        boss = self.state.npcs.get(target_id)
        if not boss or getattr(boss, "status", "在职") != "在职":
            return "你尝试向上管理，但大佬当前不在线。"
        base_trust = int(3 + player.soft_skill / 25)
        trust_min = max(2, base_trust - 2)
        trust_max = min(12, base_trust + 2)
        trust_gain = random.randint(trust_min, trust_max)
        pc_base = max(1, int(math.ceil(trust_gain / 3)))
        pc_max = pc_base + 1 if player.soft_skill >= 70 else pc_base
        pc_gain = random.randint(1, pc_max)
        boss.trust = max(0, min(100, boss.trust + trust_gain))
        player.political_capital = max(0, player.political_capital + pc_gain)
        return f"你进行了向上管理，与 {boss.name} 沟通顺畅。{boss.name} 的信任 +{trust_gain}，你的政治资本 +{pc_gain}。精力 -8。"

    def _apply_effects(self, intent: str, magnitude: float, text: str = "", channel: str = "group") -> str:
        player = self.state.player
        narrative = ""
        if not player:
            return ""

        project = self.state.projects.get(player.current_project)
        if not project and self.state.projects:
            project = next(iter(self.state.projects.values()))
            player.current_project = next(iter(self.state.projects.keys()))
        
        if intent == "WORK":
            base_energy_cost = 10
            energy_cost = int(base_energy_cost * magnitude)
            
            # Allow overwork even if energy is insufficient (triggers Game Over)
            player.energy -= energy_cost
            
            # Mood Cost: Work always consumes mood, overwork consumes more
            base_mood_cost = 2
            if magnitude >= 1.3:
                base_mood_cost = 5
            elif magnitude < 1.0:
                base_mood_cost = 1
            player.mood = max(0, player.mood - base_mood_cost)

            mood_mod = player.mood / 100.0 if player.mood > 0 else 0.1
            gear_bonus = 1.0 + 0.05 * getattr(player, "gear_gpu_level", 0) + 0.03 * getattr(player, "gear_monitor_level", 0) + 0.02 * getattr(player, "gear_chair_level", 0)
            
            kpi_gain = math.floor(
                10
                * (player.hard_skill / 50.0)
                * player.learning_rate
                * mood_mod
                * magnitude
                * gear_bonus
                * self.state.global_modifiers.get("kpi_multiplier", 1.0)
            )
            player.kpi += kpi_gain
            
            work_desc = "努力工作" if magnitude < 1.3 else "加班爆肝"
            narrative = f"你{work_desc}了一会儿。精力 -{energy_cost}, 心情 -{base_mood_cost}, KPI +{kpi_gain}。"

            if project:
                role = player.role
                base_progress = max(2, int((kpi_gain / 8) * magnitude))
                
                # Progress: Dev > Product > Ops, with simpler scaling
                if role == Role.DEV:
                    prog_gain = base_progress + 1
                elif role == Role.PRODUCT:
                    prog_gain = base_progress
                else:  # Ops
                    prog_gain = max(1, base_progress - 1)

                # 2. Risk Reduction: Ops > Product > Dev (but all can reduce)
                if role == Role.OPS:
                    risk_reduction = max(1, int(player.soft_skill / 20))
                elif role == Role.PRODUCT:
                    risk_reduction = max(1, int(player.soft_skill / 24))
                else: # Dev
                    risk_reduction = max(1, int(player.hard_skill / 45))
                
                # High magnitude (overwork) always adds risk, mitigating reduction
                if magnitude >= 1.3:
                    risk_add = int(2 * self.state.global_modifiers.get("risk_multiplier", 1.0))
                    risk_reduction -= risk_add
                
                # 3. Morale & Trust: Product/Ops > Dev
                if role == Role.PRODUCT:
                    morale_gain = int((player.soft_skill / 20) * magnitude)
                    trust_gain = int((player.soft_skill / 35) * magnitude)
                elif role == Role.OPS:
                    morale_gain = int((player.soft_skill / 25) * magnitude)
                    trust_gain = int((player.soft_skill / 40) * magnitude)
                else: # Dev
                    morale_gain = int((player.soft_skill / 50) * magnitude)
                    trust_gain = int((player.hard_skill / 80) * magnitude) # Dev earns trust via hard skill

                # 4. Bug Management: Dev reduces, others neutral/slight add
                # if role == Role.DEV:
                #     bug_fix_power = int(player.hard_skill / 40)
                #     bug_creation = random.randint(0, 2)
                #     bug_delta = bug_creation - bug_fix_power
                # else:
                #     bug_delta = random.randint(0, 1) # Non-devs generate fewer bugs but don't fix

                # Apply final values
                project.progress = min(200, project.progress + prog_gain)
                # project.bug_count = max(0, project.bug_count + bug_delta)
                
                if risk_reduction > 0:
                    project.risk = max(0, project.risk - risk_reduction)
                elif risk_reduction < 0: # Negative reduction means increase
                    project.risk = min(100, project.risk + abs(risk_reduction))
                    
                project.morale = max(0, min(100, project.morale + max(0, morale_gain)))
                project.stakeholder_trust = min(100, project.stakeholder_trust + max(0, trust_gain))
                
                # Political Capital
                pc_gain = max(0, int(risk_reduction / 3)) if risk_reduction > 0 else 0
                player.political_capital = max(0, player.political_capital + pc_gain)

                project.progress = max(0, min(100, project.progress))
                if project.progress >= 100:
                    self._complete_milestone(player.current_project, channel)
            
        elif intent == "SHOP":
            base_cost = 40
            mag = max(0.5, magnitude)
            cost = int(base_cost * mag)
            player.money -= cost

            energy_gain = int(20 * mag)
            mood_gain = max(1, int(3 + player.mood / 50))
            player.energy = min(player.max_energy, player.energy + energy_gain)
            player.mood = max(0, min(100, player.mood + mood_gain))

            narrative = f"你犒劳自己点了好东西。Money -{cost}, Energy +{energy_gain}, Mood +{mood_gain}。"

            if project:
                morale_gain = max(0, int(mood_gain / 2))
                project.morale = max(0, min(100, project.morale + morale_gain))

                risk_delta = 0
                if player.soft_skill >= 70:
                    risk_delta = -1
                elif player.soft_skill <= 40:
                    risk_delta = 1
                if risk_delta != 0:
                    project.risk = max(0, min(100, project.risk + risk_delta))
            
        elif intent == "REFUSE":
            mag = max(0.5, magnitude)
            base_energy_gain = 4
            energy_gain = int(base_energy_gain * mag)
            mood_gain = max(1, int(2 * mag))
            player.energy = min(player.max_energy, player.energy + energy_gain)
            player.mood = max(0, min(100, player.mood + mood_gain))

            narrative = f"你选择了摸鱼，暂时远离了工作。Energy +{energy_gain}, Mood +{mood_gain}。"

            if project:
                importance = 1.0 + player.hard_skill / 80.0
                prog_loss = max(0, int(2 * mag * importance))
                project.progress = max(0, project.progress - prog_loss)

                risk_add = max(1, int(1.5 * mag * (1.0 + (100 - player.soft_skill) / 100.0)))
                project.risk = min(100, project.risk + risk_add)

                morale_delta = -max(0, int(1 * mag))
                project.morale = max(0, min(100, project.morale + morale_delta))
            
        elif intent == "LEARN":
            mag = max(0.5, magnitude)
            base_cost = 80
            base_energy_cost = 20
            cost = int(base_cost * mag)
            energy_cost = int(base_energy_cost * mag)
            player.money -= cost
            player.energy -= energy_cost

            skill_gain = 1
            if player.role == Role.PRODUCT:
                player.soft_skill += skill_gain
                skill_type = "软技能"
            else:
                player.hard_skill += skill_gain
                skill_type = "硬技能"

            if project:
                if player.role == Role.PRODUCT:
                    risk_reduction = max(1, int((player.soft_skill / 32.0) * mag))
                    trust_gain = max(0, int((player.soft_skill / 50.0) * mag))
                else:
                    risk_reduction = max(1, int((player.hard_skill / 50.0) * mag))
                    trust_gain = max(0, int((player.soft_skill / 60.0) * mag))
                prog_gain = max(1, int(skill_gain * mag))

                project.progress = min(100, project.progress + prog_gain)
                project.risk = max(0, project.risk - risk_reduction)
                project.stakeholder_trust = min(100, project.stakeholder_trust + trust_gain)

            narrative = f"你抽空学习了一会儿。{skill_type} +{skill_gain}，精力 -{energy_cost}，金钱 -{cost}。"

        elif intent == "ATTACK":
            mag = max(0.5, magnitude)
            soft_mod = 1.0
            if player.soft_skill <= 40:
                soft_mod = 1.3
            elif player.soft_skill >= 70:
                soft_mod = 0.8

            trust_drop = max(1, int(3 * mag * soft_mod))
            mood_cost = max(1, int(2 * mag))
            pc_loss = max(0, int(trust_drop / 3))
            player.mood = max(0, player.mood - mood_cost)
            player.political_capital = max(0, player.political_capital - pc_loss)

            narrative = f"你发起了挑衅，气氛一度紧张。Mood -{mood_cost}。"

            if project:
                project.stakeholder_trust = max(0, project.stakeholder_trust - trust_drop)
                risk_add = max(1, int(2 * mag))
                project.risk = min(100, project.risk + risk_add)
                project.morale = max(0, project.morale - max(1, int(mag)))

        elif intent in ("SOCIAL", "SMALL_TALK"):
            base_mood = 1
            base_energy = -2
            t = (text or "").lower()
            if any(k in t for k in ["领导", "老板", "蔡总", "大伟哥"]):
                base_mood = 1
                base_energy = -3
            elif any(k in t for k in ["摸鱼", "八卦", "吃瓜"]):
                base_mood = 2
                base_energy = -1
            player.mood = max(0, min(100, player.mood + base_mood))
            player.energy = max(0, min(player.max_energy, player.energy + base_energy))
            narrative = ""
            if project:
                stake_gain = max(0, int((player.soft_skill / 30.0) * max(0.8, magnitude)))
                if any(k in t for k in ["对齐", "汇报", "同步", "沟通", "茶歇", "@", "私聊"]):
                    stake_gain = max(stake_gain, int(stake_gain * 1.2))
                project.stakeholder_trust = min(100, project.stakeholder_trust + stake_gain)
            
        return narrative

    def _kpi_grade(self, kpi: int) -> str:
        if kpi >= 4000:
            return "S"
        if kpi >= 2000:
            return "A"
        if kpi >= 1200:
            return "B"
        if kpi >= 600:
            return "C"
        return "D"

    def _project_revenue_target(self, project: Project) -> int:
        base = 50000
        if project.type == ProjectType.INFRA:
            base = 25000
        elif project.type == ProjectType.APP:
            base = 35000
        return int(base * max(1, project.difficulty))

    async def _select_topic_npcs(self, text: str, channel: str) -> list:
        player = self.state.player
        if not player or channel != "group":
            return []

        topic_res = await llm_service.extract_player_topics(text)
        raw_keywords = topic_res.get("keywords") or []
        keywords = [str(k).strip().lower() for k in raw_keywords if isinstance(k, str) and k.strip()]

        if not keywords:
            base_text = (text or "").strip()
            if not base_text:
                return []
            keywords = [base_text.lower()]

        scored = []
        for nid, npc in self.state.npcs.items():
            status = getattr(npc, "status", "在职")
            if status != "在职":
                continue

            name_str = str(getattr(npc, "name", nid) or "")
            base_name = name_str.split("（")[0].split("(")[0].strip()
            text_blob = " ".join([
                name_str,
                base_name,
                str(getattr(npc, "role", "")),
                str(getattr(npc, "traits", "")),
                str(getattr(npc, "project", "")),
            ]).lower()

            score = 0
            for kw in keywords:
                if not kw:
                    continue
                norm_kw = "".join(ch for ch in kw if not ch.isspace())
                if not norm_kw:
                    continue
                if len(norm_kw) < 2:
                    if norm_kw in text_blob:
                        score += 1
                    continue
                matched = False
                for i in range(len(norm_kw) - 1):
                    sub = norm_kw[i:i+2]
                    if sub and sub in text_blob:
                        score += 2
                        matched = True
                        break
                if not matched and norm_kw in text_blob:
                    score += 2

            if base_name and base_name in text:
                score += 5

            if score > 0:
                scored.append((score, nid))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected_ids = []
        player_project = getattr(player, "current_project", None)
        if player_project:
            same_project_ids = []
            for score, nid in scored:
                npc = self.state.npcs.get(nid)
                if not npc:
                    continue
                if getattr(npc, "project", None) == player_project:
                    same_project_ids.append(nid)
            if len(same_project_ids) >= 2:
                selected_ids = same_project_ids[:4]
        if not selected_ids:
            selected_ids = [nid for _, nid in scored[:4]]

        if len(selected_ids) == 1:
            primary_id = selected_ids[0]
            primary_npc = self.state.npcs.get(primary_id)
            if primary_npc:
                rels = getattr(primary_npc, "relations", {}) or {}
                for other_id, relation in rels.items():
                    other = self.state.npcs.get(other_id)
                    if not other:
                        continue
                    status_other = getattr(other, "status", "在职")
                    if status_other != "在职":
                        continue
                    rel_text = str(relation)
                    if any(tag in rel_text for tag in ["对立", "矛盾", "冲突", "上级", "下属"]):
                        selected_ids.append(other_id)
                        break

        if len(selected_ids) < 2:
            return []
        return selected_ids

    async def _npc_cross_talk(self, text: str, responders: list, channel: str):
        selected_ids = responders if responders else await self._select_topic_npcs(text, channel)
        if not selected_ids:
            return

        npc_payloads = []
        selected_set = set(selected_ids)
        for nid in selected_ids:
            npc = self.state.npcs.get(nid)
            if not npc:
                continue
            rels = getattr(npc, "relations", {}) or {}
            filtered_rels = {k: v for k, v in rels.items() if k in selected_set}
            npc_payloads.append({
                "id": nid,
                "name": getattr(npc, "name", nid),
                "role": getattr(npc, "role", ""),
                "traits": getattr(npc, "traits", ""),
                "project": getattr(npc, "project", ""),
                "level": getattr(npc, "level", ""),
                "relations": filtered_rels
            })

        if len(npc_payloads) < 2:
            return

        recent_group = [
            {
                "sender": msg.get("sender"),
                "content": msg.get("content"),
                "type": msg.get("type")
            }
            for msg in self.state.chat_history[-12:]
            if msg.get("target") == "group"
        ]

        llm_res = await llm_service.generate_group_crosstalk(
            text,
            self.state.player.model_dump() if hasattr(self.state.player, "model_dump") else self.state.player.dict(),
            npc_payloads,
            chat_history=recent_group
        )

        messages = llm_res.get("messages") or []
        if not messages:
            return
        if len(npc_payloads) >= 2 and len(messages) == 1:
            messages.append({"content": messages[0].get("content", "")})

        speaker_index = 0
        for item in messages:
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            npc_id = selected_ids[speaker_index % len(selected_ids)]
            npc = self.state.npcs.get(npc_id)
            if not npc:
                speaker_index += 1
                continue
            self.state.chat_history.append({
                "sender": npc.name,
                "content": content,
                "type": "npc",
                "target": channel,
                "timestamp": self._get_timestamp()
            })
            speaker_index += 1

    def _project_evolution_tick(self, channel: str):
        player = self.state.player
        if not self.state.projects:
            return

        for pid, project in self.state.projects.items():
            if project.status == ProjectStatus.CANCELED:
                continue

            cancel_pressure = 0
            if project.risk >= 95:
                cancel_pressure += 2
            elif project.risk >= 90:
                cancel_pressure += 1
            if project.morale <= 5:
                cancel_pressure += 2
            elif project.morale <= 15:
                cancel_pressure += 1
            # if project.bug_count >= 80:
            #     cancel_pressure += 1

            if cancel_pressure <= 0:
                continue

            chance = min(0.8, 0.15 * cancel_pressure)
            if project.status == ProjectStatus.LIVE:
                chance *= 0.6

            if random.random() >= chance:
                continue

            project.status = ProjectStatus.CANCELED
            project.progress = 0

            self.state.chat_history.append({
                "sender": "System",
                "content": f"{project.name} 被砍了（Risk {project.risk}/100 · Morale {project.morale}/100）。",
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            })
            self._add_fact(f"项目被砍 {project.name}")

            if player and player.current_project == pid:
                player.mood = max(0, player.mood - 15)
                for boss_id in self._get_top_executives_ids():
                    boss = self.state.npcs.get(boss_id)
                    if boss:
                        boss.trust = max(0, boss.trust - 10)

                fallback = next((k for k, p in self.state.projects.items() if p.status != ProjectStatus.CANCELED), None)
                if fallback:
                    player.current_project = fallback
                    self.state.chat_history.append({
                        "sender": "System",
                        "content": f"你被临时调配到了 {self.state.projects[fallback].name}。",
                        "type": "system",
                        "target": channel,
                        "timestamp": self._get_timestamp()
                    })

    def _complete_milestone(self, project_id: str, channel: str):
        player = self.state.player
        project = self.state.projects.get(project_id)
        if not player or not project:
            return

        was_rd = project.status == ProjectStatus.RD
        project.progress = max(0, project.progress - 100)
        base_rev = int(5000 * project.difficulty * self.state.global_modifiers.get("revenue_multiplier", 1.0))
        if was_rd:
            project.status = ProjectStatus.LIVE
            if project_id not in player.launched_projects:
                player.launched_projects.append(project_id)
            self.state.chat_history.append({
                "sender": "System",
                "content": f"{project.name} 结束研发，正式进入 Live！",
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            })
            self._add_fact(f"项目上线 {project.name}")

        target = self._project_revenue_target(project)
        if project.revenue < target:
            project.revenue += min(base_rev, max(0, target - project.revenue))
        project.risk = max(0, project.risk - 5)
        project.morale = max(0, min(100, project.morale + 5))
        project.stakeholder_trust = max(0, min(100, project.stakeholder_trust + 4))
        bonus = int(base_rev / 5)
        player.money += bonus
        player.political_capital = max(0, player.political_capital + 5)

        msg = f"{project.name} 达成阶段目标：Revenue +{base_rev}，奖金 +{bonus}，政治资本 +5。"
        self.state.chat_history.append({
            "sender": "System",
            "content": msg,
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })
        self._add_fact(f"完成 {project.name} 里程碑")

    async def _trigger_random_event(self, channel: str):
        if not self.state.player:
            return

        player = self.state.player
        level_num = self._parse_level(getattr(player, "level", "P5"))
        current_proj = getattr(player, "current_project", "General")

        candidates = []
        for ev in RANDOM_EVENTS_DB:
            # Check Level
            min_lvl = self._parse_level(ev.get("min_level", "P5"))
            if level_num < min_lvl:
                continue
            # Check Project
            ev_proj = ev.get("project", "General")
            if ev_proj != "General" and ev_proj != current_proj:
                continue
            candidates.append(ev)
        
        if not candidates:
            return

        event = random.choice(candidates)
        
        # Apply effects
        effects = event.get("effects", {})
        msg_parts = []
        
        if "mood" in effects:
            val = effects["mood"]
            player.mood = max(0, min(100, player.mood + val))
            msg_parts.append(f"Mood {'+' if val>0 else ''}{val}")
            
        if "energy" in effects:
            val = effects["energy"]
            player.energy = max(0, min(player.max_energy, player.energy + val))
            msg_parts.append(f"Energy {'+' if val>0 else ''}{val}")
            
        if "money" in effects:
            val = effects["money"]
            player.money += val
            msg_parts.append(f"Money {'+' if val>0 else ''}{val}")
            
        if "political_capital" in effects:
            val = effects["political_capital"]
            player.political_capital = max(0, player.political_capital + val)
            msg_parts.append(f"Pol.Cap {'+' if val>0 else ''}{val}")
            
        if "trust" in effects:
            val = effects["trust"]
            # Trust is usually per-NPC, but here it's global or random leader?
            # Simplified: add trust to project leader or random colleague
            pass 
            
        if "risk" in effects:
            val = effects["risk"]
            proj = self.state.projects.get(current_proj)
            if proj:
                proj.risk = max(0, proj.risk + val)
                msg_parts.append(f"Risk {'+' if val>0 else ''}{val}")

        if "progress" in effects:
            val = effects["progress"]
            proj = self.state.projects.get(current_proj)
            if proj:
                proj.progress = max(0, proj.progress + val)
                msg_parts.append(f"Progress {'+' if val>0 else ''}{val}")

        msg_content = f"{event['msg']}"
        if msg_parts:
            msg_content += f" ({', '.join(msg_parts)})"

        self.state.chat_history.append({
            "sender": "System",
            "content": msg_content,
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })

    async def _refresh_suggested_replies(self, channel: str):
        if not self.state.player:
            return
        recent = [
            {"sender": msg.get("sender"), "content": msg.get("content"), "type": msg.get("type")}
            for msg in self.state.chat_history[-8:]
        ]
        suggestions = await llm_service.generate_suggested_replies(self.state.player.dict(), recent)
        self.state.suggested_replies = suggestions[:2] if suggestions else []

    def ack_global_event(self) -> GameState:
        self.state.active_global_event = None
        return self.state

    def _check_promotion(self, channel: str):
        player = self.state.player
        if not player:
            return
        if self.state.promotion_review:
            status = self.state.promotion_review.get("status") or ""
            if status in ("pending_answer", "pending_score"):
                return

        week = getattr(self.state, "week", 0) or 0
        if week < 0:
            week = 0

        eval_weeks = {12, 24, 36, 48, 52, 60, 72, 80, 96}
        is_eval_week = week >= 12 and (week in eval_weeks or week % 12 == 0)

        def level_num(level: str) -> int:
            try:
                return int(level.replace("P", ""))
            except Exception:
                return 5

        current = level_num(player.level)
        if current >= 10:
            return

        revenue_total = sum(p.revenue for p in self.state.projects.values()) if self.state.projects else 0
        project = self.state.projects.get(player.current_project) if self.state.projects else None
        kpi = getattr(player, "kpi", 0) or 0
        pc = getattr(player, "political_capital", 0) or 0
        accidents = getattr(player, "major_accidents", 0) or 0
        participated = len(getattr(player, "participated_live_projects", []) or [])
        is_rd_project = bool(project and getattr(project, "status", None) == ProjectStatus.RD)

        can_p6 = (
            week >= 12
            and kpi >= 400
            and accidents == 0
            and (participated >= 1 or is_rd_project)
        )
        can_p7 = (
            week >= 24
            and kpi >= 1300
            and pc >= 8
            and revenue_total >= 0
        )
        can_p8 = (
            week >= 36
            and kpi >= 3000
            and pc >= 25
            and revenue_total >= 20000
            and accidents <= 1
        )
        can_p9 = (
            week >= 52
            and kpi >= 5000
            and pc >= 40
            and revenue_total >= 50000
        )
        can_p10 = (
            week >= 80
            and pc >= 80
            and revenue_total >= 200000
        )

        candidates = []
        if current < 6 and can_p6:
            candidates.append(6)
        if current < 7 and can_p7:
            candidates.append(7)
        if current < 8 and can_p8:
            candidates.append(8)
        if current < 9 and can_p9:
            candidates.append(9)
        if current < 10 and can_p10:
            candidates.append(10)

        if candidates:
            if self.state.promotion_review and (self.state.promotion_review.get("status") or "") not in ("finished",):
                return
            target_level = max(candidates)
            threshold = 55
            if target_level == 7:
                threshold = 60
            elif target_level == 8:
                threshold = 65
            elif target_level == 9:
                threshold = 70
            elif target_level >= 10:
                threshold = 72
            question_project = getattr(player, "current_project", "") or "当前项目"
            question = f"请结合你在项目 {question_project} 中的具体经历，用一段话说明你在当前阶段为团队和项目带来的关键价值，以及为什么你已经具备晋升到 P{target_level} 的能力。"
            self.state.promotion_review = {
                "status": "pending_answer",
                "target_level": target_level,
                "question": question,
                "score_threshold": threshold,
                "answer": None,
                "score": None,
                "comment": "",
            }
            msg = f"你已满足晋升至 P{target_level} 的基础条件。请围绕题目作答：{question}"
            self.state.chat_history.append({
                "sender": "System",
                "content": msg,
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            })
            return

        if not is_eval_week:
            return

        if current < 6:
            target_lvl = 6
            need = []
            if participated < 1 and not is_rd_project:
                need.append("至少参与一个已上线项目，或在预研项目中持续贡献")
            if accidents > 0:
                need.append("避免重大事故")
            if kpi < 400:
                need.append("累计更多有效KPI")
        elif current < 7:
            target_lvl = 7
            need = []
            if kpi < 1300:
                need.append("提升项目KPI贡献")
            if pc < 8:
                need.append("多与关键老板正向互动积累政治资本")
        elif current < 8:
            target_lvl = 8
            need = []
            if kpi < 3000:
                need.append("承担更大范围的核心任务")
            if pc < 25:
                need.append("在跨团队协作中建立更强话语权")
            if revenue_total < 20000:
                need.append("推动至少一个项目形成可观营收")
            if accidents > 1:
                need.append("降低重大事故发生次数")
        elif current < 9:
            target_lvl = 9
            need = []
            if kpi < 5000:
                need.append("在多个关键项目中形成稳定输出")
            if pc < 40:
                need.append("在高层视角中建立稳定信任")
            if revenue_total < 50000:
                need.append("带动更高的业务营收")
        else:
            target_lvl = 10
            need = []
            if pc < 80:
                need.append("在公司范围内形成决定性影响力")
            if revenue_total < 200000:
                need.append("推动公司级标志性业务成功")

        if not need:
            return

        msg = f"本周期暂未晋升。下一档目标：P{target_lvl}。建议：" + "；".join(need)
        self.state.chat_history.append({
            "sender": "System",
            "content": msg,
            "type": "system",
            "target": channel,
            "timestamp": self._get_timestamp()
        })

    def _check_game_over(self, channel: str):
        player = self.state.player
        if not player:
            return
        if self.state.active_global_event and not self.state.game_over:
            return
            
        reason = ""
        
        # 1. 资源耗尽 (Resource Depletion)
        if player.energy <= 0:
            reason = "Exhausted"
            self.state.game_over = True
        elif player.money < 0:
            reason = "Bankrupt"
            self.state.game_over = True
        elif player.mood <= 0:
            reason = "Depressed"
            self.state.game_over = True
            
        # 2. 长期低状态 (Chronic Low Status)
        # Check if mood/energy has been low for too long (simplified check: current status critical)
        if not self.state.game_over:
             if player.mood <= 10 and player.energy <= 20:
                 if random.random() < 0.3: # 30% chance to break down when both low
                     reason = "Breakdown"
                     self.state.game_over = True

        # 3. 社交作死 (Social Suicide)
        # Check Trust of Bosses
        if not self.state.game_over:
            bosses = [self.state.npcs[nid] for nid in self._get_top_executives_ids() if nid in self.state.npcs]
            for boss in bosses:
                if boss.trust <= 0:
                    reason = "Fired" # Offended big boss
                    self.state.game_over = True
                    break
            
            # Check Direct Manager Trust
            if not self.state.game_over and player.leader_id:
                leader = self.state.npcs.get(player.leader_id)
                if leader and leader.trust <= 0:
                    reason = "Pip" # Offended direct manager -> PIP -> Fired
                    self.state.game_over = True

        # 4. 项目组资源耗尽 (Project Failure)
        if not self.state.game_over:
            project = self.state.projects.get(player.current_project)
            if project:
                # Risk > 95 + Low Morale -> Project Collapse
                if project.risk >= 95 and project.morale <= 10:
                    reason = "ProjectCollapse"
                    self.state.game_over = True
                # Stakeholder Trust 0 -> Project Cancelled by Board
                elif project.stakeholder_trust <= 0:
                    reason = "ProjectCancelled"
                    self.state.game_over = True

        # 5. 正常通关 (Victory/Survival)
        if not self.state.game_over and self.state.week >= 52:
            revenue_total = sum(p.revenue for p in self.state.projects.values()) if self.state.projects else 0
            if player.kpi >= 5000 and player.political_capital >= 30:
                reason = "Executive"
                self.state.game_over = True
            elif player.money >= 60000:
                reason = "Rich"
                self.state.game_over = True
            elif revenue_total >= 100000 and player.kpi >= 3500:
                reason = "Producer"
                self.state.game_over = True
            else:
                reason = "Stable"
                self.state.game_over = True
                
        if self.state.game_over:
            self.state.ending = reason
            msg_map = {
                "Exhausted": "你累倒了，被送进了ICU...（过劳结局）",
                "Bankrupt": "你的存款归零，无力支付房租，只能回老家了...（破产结局）",
                "Depressed": "长期心情低落让你患上了抑郁，医生建议你长期休假...（抑郁结局）",
                "Breakdown": "身心俱疲的你终于崩溃了，在工位上大哭一场后离职...（崩溃结局）",
                "Fired": "因为得罪了大老板，你收到了辞退通知书。保安已在路上...（被裁结局）",
                "Pip": "直属领导对你彻底失望，PIP 考核未通过，你被劝退了...（PIP结局）",
                "ProjectCollapse": "项目彻底崩盘，作为核心成员的你被迫背锅离职...（背锅结局）",
                "ProjectCancelled": "资方对项目彻底失去信任，项目组原地解散，你失业了...（解散结局）",
                "Executive": "你在组织里站稳了脚跟，成为了高管。下一站：改变世界。",
                "Rich": "你靠奖金与投资实现了财富自由，提前退休去环游世界。",
                "Producer": "你带队做出爆款，成了金牌制作人，所有人都来找你借人。",
                "Stable": "你平稳度过了一年，成为了靠谱的中坚力量。",
            }
            msg = msg_map.get(reason, f"游戏结束 ({reason})。")
            self.state.chat_history.append({
                "sender": "System",
                "content": msg,
                "type": "system",
                "target": channel,
                "timestamp": self._get_timestamp()
            })

game_manager = GameManager()
