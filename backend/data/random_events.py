
# 随机事件库 (内置 50 个)
# 触发条件: min_level (最低职级 P5-P8), project (特定项目或 General)
# type: 'positive' | 'negative' | 'neutral'

RANDOM_EVENTS_DB = [
    # --- General (All) ---
    {
        "id": "evt_001",
        "msg": "茶水间遇到大伟哥，被夸奖最近精神不错。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 10, "political_capital": 2}
    },
    {
        "id": "evt_002",
        "msg": "楼下自动贩卖机多吐了一瓶快乐水，心情大好。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 5, "energy": 2}
    },
    {
        "id": "evt_003",
        "msg": "突然发现工位网线松了，排查半小时才发现没网。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -5, "energy": -2}
    },
    {
        "id": "evt_004",
        "msg": "行政小姐姐发了下午茶，是喜茶限定款。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 8, "energy": 5}
    },
    {
        "id": "evt_005",
        "msg": "在这个点竟然打到了车，不用排队，奇迹！",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 5}
    },
    {
        "id": "evt_006",
        "msg": "耳机坏了一边，写代码时感觉只有半个脑子在转。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -3}
    },
    {
        "id": "evt_007",
        "msg": "参加技术分享会，虽然没听懂但抢到了红包。",
        "min_level": "P5",
        "project": "General",
        "effects": {"money": 50, "mood": 2}
    },
    {
        "id": "evt_008",
        "msg": "因为没带工牌被保安拦下，迟到了5分钟。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -5}
    },
    {
        "id": "evt_009",
        "msg": "发现健身房新换了器材，虽然你并不打算去练。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 1}
    },
    {
        "id": "evt_010",
        "msg": "收到神秘快递，原来是之前买的手办到了。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 15, "money": -200}
    },

    # --- Level P5-P6 (Junior/Mid) ---
    {
        "id": "evt_011",
        "msg": "提交的代码一次性通过 Code Review，简直不敢相信。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 10, "trust": 2}
    },
    {
        "id": "evt_012",
        "msg": "被分配去修一个陈年老Bug，看代码像是在考古。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -5, "energy": -5}
    },
    {
        "id": "evt_013",
        "msg": "导师请客吃火锅，虽然是AA但感觉赚了。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 5, "money": -50}
    },
    {
        "id": "evt_014",
        "msg": "因为写错一个标点符号导致线上报警，被吓出一身冷汗。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -10, "risk": 2}
    },
    {
        "id": "evt_015",
        "msg": "帮忙搬运新到的测试机，获得了行政部的感谢。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 3, "political_capital": 1}
    },

    # --- Level P7+ (Senior) ---
    {
        "id": "evt_016",
        "msg": "跨部门撕逼大获全胜，对方产品经理哑口无言。",
        "min_level": "P7",
        "project": "General",
        "effects": {"mood": 15, "political_capital": 5}
    },
    {
        "id": "evt_017",
        "msg": "被拉进一个没有任何产出的全天会议，感觉生命在流逝。",
        "min_level": "P7",
        "project": "General",
        "effects": {"mood": -15, "energy": -10}
    },
    {
        "id": "evt_018",
        "msg": "你的技术方案被作为部门标杆进行推广。",
        "min_level": "P7",
        "project": "General",
        "effects": {"trust": 10, "political_capital": 10}
    },
    {
        "id": "evt_019",
        "msg": "猎头打来电话挖角，虽然没去但虚荣心得到了满足。",
        "min_level": "P7",
        "project": "General",
        "effects": {"mood": 5}
    },
    {
        "id": "evt_020",
        "msg": "需要在老板面前做紧急汇报，PPT还没写完。",
        "min_level": "P7",
        "project": "General",
        "effects": {"mood": -10, "energy": -5}
    },

    # --- Project: Genshin ---
    {
        "id": "evt_021",
        "msg": "原神新版本PV发布，全网好评，团队士气大振。",
        "min_level": "P5",
        "project": "Genshin",
        "effects": {"mood": 10, "morale": 5}
    },
    {
        "id": "evt_022",
        "msg": "因为圣遗物掉率问题被玩家炎上，策划组气氛压抑。",
        "min_level": "P5",
        "project": "Genshin",
        "effects": {"mood": -5, "morale": -2}
    },
    {
        "id": "evt_023",
        "msg": "测试服发现严重穿模Bug，美术组连夜加班。",
        "min_level": "P5",
        "project": "Genshin",
        "effects": {"energy": -10, "risk": 5}
    },

    # --- Project: Honkai3 ---
    {
        "id": "evt_024",
        "msg": "崩坏3剧情刀片太多，收到玩家寄来的“土特产”。",
        "min_level": "P5",
        "project": "Honkai3",
        "effects": {"mood": 2, "morale": 2}
    },
    {
        "id": "evt_025",
        "msg": "老舰长回归活动数据超预期，运营组请喝奶茶。",
        "min_level": "P5",
        "project": "Honkai3",
        "effects": {"mood": 5, "energy": 5}
    },

    # --- Project: HSR (StarRail) ---
    {
        "id": "evt_026",
        "msg": "星穹铁道由于文案太有梗，上了热搜。",
        "min_level": "P5",
        "project": "HSR",
        "effects": {"mood": 8, "political_capital": 2}
    },
    {
        "id": "evt_027",
        "msg": "回合制战斗节奏被吐槽太慢，策划连夜调整倍速。",
        "min_level": "P5",
        "project": "HSR",
        "effects": {"energy": -5, "risk": -2}
    },

    # --- Project: ZZZ ---
    {
        "id": "evt_028",
        "msg": "绝区零的打击感调试由于手感太好，全组都在摸鱼试玩。",
        "min_level": "P5",
        "project": "ZZZ",
        "effects": {"mood": 10, "progress": -5}
    },
    {
        "id": "evt_029",
        "msg": "由于美术风格太潮，被隔壁组借去参考（抄袭）。",
        "min_level": "P5",
        "project": "ZZZ",
        "effects": {"political_capital": 3}
    },

    # --- Project: IAM/Infra ---
    {
        "id": "evt_030",
        "msg": "IAM 鉴权服务 502，全公司无法登录，SRE 正在尖叫。",
        "min_level": "P5",
        "project": "IAM",
        "effects": {"mood": -20, "risk": 20}
    },
    {
        "id": "evt_031",
        "msg": "成功拦截一次大规模爬虫攻击，安全组受到表彰。",
        "min_level": "P5",
        "project": "IAM",
        "effects": {"mood": 10, "political_capital": 5}
    },
    {
        "id": "evt_032",
        "msg": "新上线的SSO体验丝滑，收到其他项目组的感谢信。",
        "min_level": "P5",
        "project": "IAM",
        "effects": {"trust": 5, "morale": 5}
    },

    # --- Mixed/Misc ---
    {
        "id": "evt_033",
        "msg": "食堂今天的红烧肉特别好吃。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 5, "energy": 5}
    },
    {
        "id": "evt_034",
        "msg": "下雨天没带伞，被淋成落汤鸡。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -10, "energy": -5}
    },
    {
        "id": "evt_035",
        "msg": "电脑突然蓝屏，刚才写的代码没保存。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -20, "progress": -2}
    },
    {
        "id": "evt_036",
        "msg": "隔壁工位的小猫咪今天来上班了，疯狂吸猫。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 15, "progress": -1}
    },
    {
        "id": "evt_037",
        "msg": "收到一笔莫名的报销款，意外之财。",
        "min_level": "P5",
        "project": "General",
        "effects": {"money": 200, "mood": 5}
    },
    {
        "id": "evt_038",
        "msg": "被选中参加新游戏保密测试，感觉像在做特务。",
        "min_level": "P6",
        "project": "General",
        "effects": {"mood": 5}
    },
    {
        "id": "evt_039",
        "msg": "因为文档写得太好，被当做模板全公司推广。",
        "min_level": "P6",
        "project": "General",
        "effects": {"political_capital": 5, "trust": 5}
    },
    {
        "id": "evt_040",
        "msg": "由于长期坐姿不正，腰椎间盘突出犯了。",
        "min_level": "P6",
        "project": "General",
        "effects": {"energy": -15, "mood": -5}
    },
    {
        "id": "evt_041",
        "msg": "发现自己的代码被别的组 copy 且没有注明出处。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -5}
    },
    {
        "id": "evt_042",
        "msg": "在大群里发错表情包，瞬间撤回但已被截图。",
        "min_level": "P5",
        "project": "General",
        "effects": {"political_capital": -2, "mood": -5}
    },
    {
        "id": "evt_043",
        "msg": "参加黑客马拉松，拿了个参与奖。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 2, "money": 100}
    },
    {
        "id": "evt_044",
        "msg": "由于系统维护，今晚不用发版，提前下班！",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 10, "energy": 5}
    },
    {
        "id": "evt_045",
        "msg": "由于系统故障，今晚被迫通宵支持。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -20, "energy": -30}
    },
    {
        "id": "evt_046",
        "msg": "路过会议室听到老板在夸你。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 15, "trust": 5}
    },
    {
        "id": "evt_047",
        "msg": "路过会议室听到老板在吐槽你。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -15, "trust": -5}
    },
    {
        "id": "evt_048",
        "msg": "你的工位被调整到了空调出风口，冷得瑟瑟发抖。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -5, "energy": -2}
    },
    {
        "id": "evt_049",
        "msg": "公司发的节日礼盒里竟然有金条（巧克力做的）。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": 5}
    },
    {
        "id": "evt_050",
        "msg": "突然想起还没有填周报，惊坐起。",
        "min_level": "P5",
        "project": "General",
        "effects": {"mood": -5}
    }
]
