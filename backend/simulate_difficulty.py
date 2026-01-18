import asyncio
import random
from game import GameManager, OnboardRequest, Role
from collections import Counter

# 模拟参数
# 10分钟游戏时间 ≈ 20周 (假设一周30秒)
SIMULATION_WEEKS = 20 
SIMULATION_COUNT = 100

async def run_simulation(strategy_name, strategy_func):
    outcomes = []
    promotion_weeks = []
    game_over_weeks = []
    
    for i in range(SIMULATION_COUNT):
        gm = GameManager()
        await gm.init_game(OnboardRequest(name=f"SimPlayer_{i}", role=Role.DEV, project_name="Genshin"))
        player = gm.state.player
        
        promoted = False
        initial_level = player.level
        
        # Debug first case
        debug = (i == 0)
        if debug:
            print(f"DEBUG: {strategy_name} Start - Money: {player.money}, Energy: {player.energy}")
        
        max_turns = SIMULATION_WEEKS * 7
        turn = 0
        
        while gm.state.week <= SIMULATION_WEEKS:
            if gm.state.game_over:
                break
            
            turn += 1
            if turn > max_turns:
                break
            
            # Decide action
            action_type, arg = strategy_func(gm)
            
            if debug and turn <= 14: # Print first 2 weeks detail
                print(f"  Week {gm.state.week} Day {gm.state.day_of_week}: {action_type} {arg} | E:{player.energy} M:{player.money} Mood:{player.mood} KPI:{player.kpi}")

            # Execute action
            if action_type == "work":
                gm._apply_effects("WORK", arg, channel="group")
            elif action_type == "chat":
                gm._apply_effects("SOCIAL", 1.0, text=arg, channel="group")
            elif action_type == "rest":
                gm._apply_effects("REFUSE", 1.0, channel="group")
            elif action_type == "rice":
                gm._apply_rice_item(arg)
            elif action_type == "shop":
                gm._apply_shop_item(arg, channel="group")
            elif action_type == "course":
                gm._apply_academy_course(arg, channel="group")

            # Advance time (1 day)
            gm._advance_time("group", days=1)
            
            # Check promotion
            if not promoted and player.level != initial_level:
                promoted = True
                promotion_weeks.append(gm.state.week)
                if debug:
                    print(f"DEBUG: Promoted to {player.level} at Week {gm.state.week}")
        
        if gm.state.game_over:
            outcomes.append(gm.state.ending)
            game_over_weeks.append(gm.state.week)
            if debug:
                print(f"DEBUG: Game Over at Week {gm.state.week}: {gm.state.ending}")
        else:
            outcomes.append("Survived")
            if debug:
                print(f"DEBUG: Survived. Final Money: {player.money}, KPI: {player.kpi}, Level: {player.level}")
            
    return outcomes, promotion_weeks, game_over_weeks

def strategy_random_noob(gm):
    """
    瞎玩策略：随机行动，不顾死活。
    模拟完全不懂机制的新手。
    """
    roll = random.random()
    p = gm.state.player
    
    # 极高概率乱花钱或乱加班
    if roll < 0.3:
        return "work", 1.5 # 疯狂加班 (Overwork)
    elif roll < 0.5:
        return "shop", "gift" # 乱买礼物
    elif roll < 0.6:
        return "shop", "gpu" # 试图买显卡(可能买不起)
    elif roll < 0.7:
        return "chat", "摸鱼"
    elif roll < 0.8:
        return "rice", "luxury" # 吃太贵
    else:
        return "work", 1.0

def strategy_cruncher(gm):
    """
    卷王策略：只知道工作，不顾身体。
    模拟头铁玩家。
    """
    p = gm.state.player
    # 只要没死就工作
    if p.energy > 5:
        return "work", 1.5
    else:
        # 实在没体力了才休息一下
        return "rest", ""

def strategy_pro(gm):
    """
    高手策略：数值管理大师。
    目标：生存并晋升。
    """
    p = gm.state.player
    
    # 0. 优先购买增益道具 (Early Game Investment)
    # 买咖啡月卡 (性价比高)
    if "shop:coffee_pass" not in p.workbench_purchases and p.money >= 260:
        return "shop", "coffee_pass"
    
    # 1. 生存红线 (Survival First)
    if p.energy <= 20:
        if p.money >= 30: return "rice", "standard" # 吃普通餐回血
        return "rest", "" # 没钱就睡觉
    
    if p.mood <= 20:
        if p.money >= 50: return "rice", "afternoon_tea" # 下午茶回心情
        return "chat", "摸鱼" # 没钱就摸鱼
        
    # 2. 状态维持 (Maintenance)
    # 保持心情和体力在较高水平以获得 KPI 加成
    if p.mood < 70:
        return "chat", "摸鱼" # 低成本回心情
        
    if p.energy < 60:
        if p.money >= 30: return "rice", "standard"
        return "rest", ""

    # 3. 装备升级 (Gear Up)
    # 有闲钱就买装备提升效率
    if p.money > 3000 and "shop:monitor" not in p.workbench_purchases:
        return "shop", "monitor"
        
    # 4. 推进工作 (Push)
    # 状态好时全力输出
    if p.energy > 80 and p.mood > 80:
        return "work", 1.5 # 状态好，加班效率高
        
    return "work", 1.0 # 正常工作

async def main():
    strategies = [
        ("Random Noob (瞎玩)", strategy_random_noob),
        ("Cruncher (卷王)", strategy_cruncher),
        ("Pro (高手)", strategy_pro)
    ]
    
    print(f"{'='*10} 20周(约10分钟)生存模拟 (N={SIMULATION_COUNT}) {'='*10}\n")
    
    results = []
    
    for name, func in strategies:
        outcomes, promo_weeks, death_weeks = await run_simulation(name, func)
        counter = Counter(outcomes)
        survived = counter["Survived"]
        died = SIMULATION_COUNT - survived
        death_rate = (died / SIMULATION_COUNT) * 100
        promo_rate = (len(promo_weeks) / SIMULATION_COUNT) * 100
        
        avg_death = sum(death_weeks)/len(death_weeks) if death_weeks else 0
        avg_promo = sum(promo_weeks)/len(promo_weeks) if promo_weeks else 0
        
        print(f"策略: {name}")
        print(f"  死亡率: {death_rate:.1f}% (目标: ~70% for Noobs)")
        print(f"  晋升率: {promo_rate:.1f}% (目标: Pro > 0%)")
        print(f"  平均死亡周: {avg_death:.1f}")
        if promo_weeks:
            print(f"  平均晋升周: {avg_promo:.1f}")
        print(f"  结局分布: {dict(counter)}")
        print("-" * 30)
        
        results.append({
            "name": name,
            "death_rate": death_rate,
            "promo_rate": promo_rate
        })

if __name__ == "__main__":
    asyncio.run(main())
