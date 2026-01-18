import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, MessageSquare, Briefcase, ShoppingBag, Coffee, Search, Users } from 'lucide-react';

const API_URL = (import.meta.env.VITE_API_BASE_URL || "/api");

const mapRoleToCN = (role) => {
  if (!role) return "";
  const r = String(role);
  if (r === "Dev") return "研发";
  if (r === "Product") return "产品";
  if (r === "Ops") return "运营";
  if (r === "CTO") return "技术负责人";
  if (r === "CEO") return "总裁";
  return r;
};

const mapProjectToCN = (projectId) => {
  if (!projectId) return "";
  const p = String(projectId);
  if (p === "Genshin") return "原神";
  if (p === "Honkai3") return "崩坏3";
  if (p === "HSR") return "星穹铁道";
  if (p === "ZZZ") return "绝区零";
  if (p === "HYG") return "神秘新作";
  if (p === "IAM") return "iam";
  if (p === "General") return "公共项目";
  if (p === "HR") return "人力资源";
  return p;
};

// NPC List (Fallback)
const NPC_LIST_FALLBACK = [
  { id: 'Cai', name: 'Cai (蔡总)', role: 'CTO', avatar: 'C', bg: 'bg-indigo-500' },
  { id: 'Dawei', name: 'Dawei (大伟哥)', role: 'CEO', avatar: 'D', bg: 'bg-yellow-500' },
];

function App() {
  const [gameState, setGameState] = useState(null);
  const [npcList, setNpcList] = useState(NPC_LIST_FALLBACK);
  const [input, setInput] = useState("");
  const [onboardData, setOnboardData] = useState({ name: "", role: "Dev", project_name: "Genshin" });
  const [isOnboarding, setIsOnboarding] = useState(true);
  const [selectedChat, setSelectedChat] = useState('group'); // 'group' or NPC ID
  const [currentView, setCurrentView] = useState('chat'); // 'chat' or 'workbench'
  const [searchQuery, setSearchQuery] = useState("");
  const [showProfile, setShowProfile] = useState(false);
  const [showShop, setShowShop] = useState(false);
  const [showAcademy, setShowAcademy] = useState(false);
  const [showRice, setShowRice] = useState(false);
  const [loading, setLoading] = useState(false); // Global loading for onboard/commands
  const [isTyping, setIsTyping] = useState(false); // Chat stream typing indicator
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, msg: null });
  
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const searchInputRef = useRef(null);

  const formatTime = (isoString) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getLastMsgTime = (targetId, isGroup = false) => {
    if (!gameState?.chat_history) return null;
    
    const history = gameState.chat_history;
    const lastMsg = [...history].reverse().find(msg => {
      if (isGroup) {
        return !msg.target || msg.target === 'group';
      } else {
        const npc = npcList.find(n => n.id === targetId);
        if (!npc) return false;
        return (msg.sender === npc.name) || (msg.target === targetId);
      }
    });
    
    return lastMsg ? formatTime(lastMsg.timestamp) : null;
  };

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [gameState?.chat_history, selectedChat, currentView]);

  // Sync NPC data from backend when game state updates
  useEffect(() => {
    if (gameState?.npcs) {
      const backendNpcs = Object.entries(gameState.npcs).map(([key, data]) => {
        // Map backend NPC data to UI format
        // Consistent color mapping based on ID char code
        const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-teal-500', 'bg-blue-500', 'bg-indigo-500', 'bg-purple-500', 'bg-pink-500'];
        const colorIdx = key.charCodeAt(0) % colors.length;
        
        return {
          id: key,
          name: data.name,
          role: data.role,
          avatar: data.name[0].toUpperCase(),
          bg: colors[colorIdx]
        };
      });
      if (backendNpcs.length > 0) {
        setNpcList(backendNpcs);
      }
    }
  }, [gameState]);

  const handleOnboard = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/init`, onboardData);
      setGameState(res.data);
      setIsOnboarding(false);
    } catch (err) {
      console.error(err);
      alert("启动失败，请检查后端服务是否运行");
    } finally {
      setLoading(false);
    }
  };

  const sendCommand = async (cmd) => {
    if (gameState?.game_over) return;
    try {
      const res = await axios.post(`${API_URL}/action`, { 
        action_type: "chat", 
        content: `cmd:${cmd}`,
        target_npc: "group"
      });
      setGameState(res.data);
    } catch (err) {
      console.error(err);
    }
  };
  
  const sendWorkbenchCommand = async (cmd) => {
    if (gameState?.game_over) return;
    try {
      const res = await axios.post(`${API_URL}/action`, {
        action_type: "workbench",
        content: `cmd:${cmd}`,
        target_npc: "workbench"
      });
      setGameState(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || gameState?.game_over) return;
    const msg = input;
    setInput("");
    setIsTyping(true); // Start typing indicator
    
    // Optimistic Update (will be replaced/confirmed by stream)
    const tempState = { ...gameState };
    // Do not append here if we trust the stream to confirm it immediately?
    // Actually, stream sends 'msg_append' for player message too.
    // So we can wait or show a pending state. 
    // Let's rely on stream for consistency, but maybe show it grayed out?
    // For now, let's just let the stream handle it to avoid duplication if we don't dedupe.
    // Wait, previous logic had optimistic update. 
    // If we remove it, user sees nothing for a split second.
    // But our backend stream yields player message confirmation first thing.
    // So latency should be low.
    
    try {
      const target = selectedChat === 'group' ? null : selectedChat;
      
      const response = await fetch(`${API_URL}/action/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          action_type: "chat", 
          content: msg,
          target_npc: target 
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr === '[DONE]') break;
            
            try {
              const data = JSON.parse(dataStr);
              
              setGameState(prevState => {
                if (!prevState) return prevState;
                const newState = { ...prevState };
                
                if (data.type === 'msg_append') {
                  // Check if msg already exists (dedupe by timestamp + content + sender)
                  // Simple check: is last message identical?
                  const lastMsg = newState.chat_history[newState.chat_history.length - 1];
                  const isDuplicate = lastMsg && 
                                      lastMsg.timestamp === data.msg.timestamp && 
                                      lastMsg.content === data.msg.content;
                  
                  if (!isDuplicate) {
                    newState.chat_history = [...newState.chat_history, data.msg];
                  }
                } else if (data.type === 'msg_update') {
                    // Update the last message (e.g. sender name resolution)
                    const lastIdx = newState.chat_history.length - 1;
                    if (lastIdx >= 0) {
                        newState.chat_history[lastIdx] = data.msg;
                        newState.chat_history = [...newState.chat_history]; // Trigger re-render
                    }
                } else if (data.type === 'state_update') {
                  return data.state; // Full state update
                } else if (data.type === 'error') {
                  alert(data.content);
                }
                
                return newState;
              });
            } catch (e) {
              console.error("Parse error", e);
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
        setIsTyping(false); // Stop typing indicator
    }
  };

  const applyQuickReply = (text) => {
    if (!text || gameState?.game_over) return;
    setInput(text);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleMsgContextMenu = (event, msg) => {
    event.preventDefault();
    if (msg.type === 'player' || msg.type === 'system') return;
    setContextMenu({
      visible: true,
      x: event.clientX,
      y: event.clientY,
      msg,
    });
  };

  const handleContextMenuClose = () => {
    setContextMenu({ visible: false, x: 0, y: 0, msg: null });
  };

  const handleContextMenuAt = () => {
    if (!contextMenu.msg) return;
    const senderName = contextMenu.msg.sender;
    const npc = npcList.find(n => n.name === senderName);
    const mention = npc ? `@${npc.name}` : `@${senderName}`;
    setSelectedChat('group');
    setInput(prev => {
      if (!prev || !prev.trim()) return `${mention} `;
      return `${prev.trim()} ${mention} `;
    });
    handleContextMenuClose();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleContextMenuCopy = () => {
    if (!contextMenu.msg) return;
    if (navigator.clipboard && contextMenu.msg.content) {
      navigator.clipboard.writeText(contextMenu.msg.content);
    }
    handleContextMenuClose();
  };
  
  const handleRestart = () => {
    setIsOnboarding(true);
    setGameState(null);
  };

  const filteredNPCs = (() => {
    if (!npcList || npcList.length === 0) return [];
    const history = gameState?.chat_history || [];
    const lowerQuery = (searchQuery || "").toLowerCase();

    const withLast = npcList.map(npc => {
      const last = [...history].reverse().find(msg => {
        if (!msg) return false;
        const npcName = npc.name;
        const npcId = npc.id;
        if (msg.type === 'npc' && msg.sender === npcName) return true;
        if (msg.type === 'player' && msg.target === npcId) return true;
        return false;
      });
      return {
        ...npc,
        lastTimestamp: last ? last.timestamp : null,
      };
    });

    if (!lowerQuery) {
      return withLast
        .filter(n => n.lastTimestamp)
        .sort((a, b) => {
          if (!a.lastTimestamp || !b.lastTimestamp) return 0;
          return new Date(b.lastTimestamp) - new Date(a.lastTimestamp);
        });
    }

    return withLast
      .filter(n => n.name.toLowerCase().includes(lowerQuery))
      .sort((a, b) => {
        if (a.lastTimestamp && b.lastTimestamp) {
          return new Date(b.lastTimestamp) - new Date(a.lastTimestamp);
        }
        if (a.lastTimestamp) return -1;
        if (b.lastTimestamp) return 1;
        return 0;
      });
  })();

  const filteredMessages = gameState?.chat_history.filter(msg => {
    // If selectedChat is 'group', show group messages (target='group' or null)
    if (selectedChat === 'group') return !msg.target || msg.target === 'group';
    // If selectedChat is NPC, show DM messages (target=NPC_ID)
    return msg.target === selectedChat;
  }) || [];

  const activeNpcCount = (() => {
    if (!gameState?.chat_history) return 0;
    const recent = gameState.chat_history.slice(-20);
    const names = recent.filter(msg => msg.type === 'npc').map(msg => msg.sender);
    return Array.from(new Set(names)).length;
  })();

  // Project Config
  const PROJECTS = [
    { id: "Genshin", name: "原神", status: "Live", statusCN: "已上线", risk: "高压", desc: "技术宅拯救世界" },
    { id: "Honkai3", name: "崩坏3", status: "Live", statusCN: "已上线", risk: "稳定", desc: "为世界上所有的美好而战" },
    { id: "HSR", name: "星穹铁道", status: "RD", statusCN: "预研", risk: "冲刺", desc: "银河冒险之旅" },
    { id: "ZZZ", name: "绝区零", status: "RD", statusCN: "预研", risk: "创新", desc: "潮流动作新游" },
  { id: "HYG", name: "神秘新作", status: "Pre", statusCN: "预研", risk: "高风险", desc: "神秘新作" },
  { id: "IAM", name: "iam", status: "Live", statusCN: "已上线", risk: "基建", desc: "通行证与基础设施" },
  ];

  const ROLES = [
    { id: "Product", name: "产品经理", icon: <Briefcase className="w-6 h-6"/>, desc: "统筹规划，平衡需求" },
    { id: "Dev", name: "研发工程师", icon: <Coffee className="w-6 h-6"/>, desc: "代码构建虚拟世界" },
    { id: "Ops", name: "综合运营", icon: <Users className="w-6 h-6"/>, desc: "维护社区与用户体验" },
  ];
  
  const RICE_OPTIONS = [
    { id: "light", name: "速食简餐", summary: "¥15 · 精力 +10 · 心情 +2 · 小概率悟性提升", emoji: "🍱" },
    { id: "standard", name: "普通套餐", summary: "¥30 · 精力 +20 · 心情 +5 · 有机会悟性+0.05", emoji: "🍛" },
    { id: "luxury", name: "豪华犒劳", summary: "¥80 · 精力 +30 · 心情 +15 · 高概率悟性+0.1", emoji: "🥩" },
    { id: "midnight", name: "深夜加班餐", summary: "¥45 · 精力 +25 · 心情 -3 · 加班灵感触发", emoji: "🍜" },
    { id: "healthy", name: "健身餐", summary: "¥55 · 精力 +18 · 心情 +6 · 清爽提神", emoji: "🥗" },
    { id: "salad", name: "减脂沙拉", summary: "¥40 · 精力 +8 · 心情 +4 · 轻量但不失营养", emoji: "🥙" },
    { id: "spicy", name: "超辣冒菜", summary: "¥38 · 精力 +18 · 心情 +8 · 辣到思路清晰", emoji: "🌶️" },
    { id: "buffet", name: "自助餐券", summary: "¥98 · 精力 +35 · 心情 +18 · P6 解锁 · 高概率悟性提升", emoji: "🍽️" },
    { id: "afternoon_tea", name: "下午茶点心", summary: "¥28 · 精力 +6 · 心情 +10 · 适合摸鱼小憩", emoji: "🧁" },
    { id: "breakfast_combo", name: "早餐大礼包", summary: "¥25 · 精力 +15 · 心情 +5 · 早起玩家专属", emoji: "🥐" },
    { id: "late_snack", name: "夜宵炸鸡", summary: "¥42 · 精力 +16 · 心情 +12 · 深夜团建必备", emoji: "🍗" },
    { id: "team_lunch", name: "项目组团建午餐", summary: "¥65 · 精力 +20 · 心情 +15 · 限购 · 提升氛围", emoji: "🍻" },
    { id: "hidden_menu", name: "食堂隐藏菜单", summary: "¥32 · 精力 +22 · 心情 +8 · 限购 · 熟人专享", emoji: "🍲" },
    { id: "fruit_plate", name: "办公室水果拼盘", summary: "¥30 · 精力 +8 · 心情 +10 · 维生素补给", emoji: "🍇" },
    { id: "brain_soup", name: "养生鸡汤", summary: "¥36 · 精力 +18 · 心情 +8 · 有机会悟性+0.1", emoji: "🍲" },
    { id: "congee", name: "养胃小米粥", summary: "¥18 · 精力 +12 · 心情 +6 · 熬夜后回血", emoji: "🥣" },
    { id: "ramen", name: "深夜拉面", summary: "¥35 · 精力 +18 · 心情 +9 · 深夜食堂限定", emoji: "🍜" },
    { id: "bento", name: "自带便当", summary: "¥0 · 精力 +14 · 心情 +7 · 有机会悟性+0.05", emoji: "🍱" },
    { id: "mystery_meal", name: "神秘今日特餐", summary: "¥33 · 精力 +16 · 心情 +6 · 厨师推荐 · 悟性随机提升", emoji: "❓" },
    { id: "brain_buffet", name: "脑力自助餐", summary: "¥120 · 精力 +28 · 心情 +18 · P6 解锁 · 必定悟性+0.2 · 限购", emoji: "🧠" },
    { id: "cheap_snack", name: "办公零食凑合吃", summary: "¥10 · 精力 +6 · 心情 +3 · 小概率突然开窍", emoji: "🍘" },
  ];

  const SHOP_ITEMS_UI = [
    { id: "gift", name: "限量手办礼物", summary: "¥200 · 提升同事/老板信任 · 部分提升政治资本 · 限购", note: "cmd:shop:gift", emoji: "🎁" },
    { id: "gpu", name: "显卡升级", summary: "¥3000 · 硬技能 +3 · 显卡等级 +1", note: "cmd:shop:gpu", emoji: "🖥️" },
    { id: "monitor", name: "显示器升级", summary: "¥2000 · 心情 +5 · 显示器等级 +1", note: "cmd:shop:monitor", emoji: "💻" },
    { id: "chair", name: "工学椅升级", summary: "¥1500 · 最大精力 +10 · 精力 +10 · 椅子等级 +1", note: "cmd:shop:chair", emoji: "💺" },
    { id: "coffee_pass", name: "咖啡月卡", summary: "¥260 · 多次稳定续命 · 有概率提升悟性 · 限购", note: "cmd:shop:coffee_pass", emoji: "☕" },
    { id: "snack_box", name: "零食补给箱", summary: "¥120 · 心情 +10 · 工位幸福感提升", note: "cmd:shop:snack_box", emoji: "🍿" },
    { id: "massage_coupon", name: "按摩理疗券", summary: "¥180 · 精力 +20 · 心情 +8", note: "cmd:shop:massage_coupon", emoji: "💆" },
    { id: "noise_headphone", name: "降噪耳机", summary: "¥2200 · 高概率悟性+0.1 · 专注度提升", note: "cmd:shop:noise_headphone", emoji: "🎧" },
    { id: "standing_desk", name: "升降桌", summary: "¥2800 · 精力 +10 · 心情 +6 · 有概率悟性提升 · P6 推荐", note: "cmd:shop:standing_desk", emoji: "🧍" },
    { id: "plant", name: "工位绿植", summary: "¥60 · 心情 +6 · 轻度治愈", note: "cmd:shop:plant", emoji: "🪴" },
    { id: "keyboard", name: "机械键盘", summary: "¥700 · 心情 +5 · 敲击体验提升", note: "cmd:shop:keyboard", emoji: "⌨️" },
    { id: "mouse", name: "人体工学鼠标", summary: "¥350 · 精力 +5 · 手腕负担降低", note: "cmd:shop:mouse", emoji: "🖱️" },
    { id: "desk_lamp", name: "护眼台灯", summary: "¥280 · 有概率悟性+0.05 · 加班不伤眼", note: "cmd:shop:desk_lamp", emoji: "💡" },
    { id: "book_pack_hard", name: "硬核技术书单", summary: "¥400 · 硬技能 +2 · 有概率悟性+0.1", note: "cmd:shop:book_pack_hard", emoji: "📚" },
    { id: "book_pack_soft", name: "管理沟通书单", summary: "¥380 · 软技能 +2 · 有概率悟性+0.1", note: "cmd:shop:book_pack_soft", emoji: "📖" },
    { id: "cloud_subscription", name: "云服务订阅", summary: "¥520 · 硬技能 +1 · 个人项目生产力提升", note: "cmd:shop:cloud_subscription", emoji: "☁️" },
    { id: "ai_toolkit", name: "AI 助手工具包", summary: "¥980 · 硬/软技能小幅提升 · 必定悟性+0.15 · 限购", note: "cmd:shop:ai_toolkit", emoji: "🤖" },
    { id: "team_snack", name: "团队下午茶", summary: "¥260 · 心情 +15 · 政治资本 +2 · 限购", note: "cmd:shop:team_snack", emoji: "🧋" },
    { id: "lucky_draw", name: "盲盒福袋", summary: "¥66 · 心情 +10 · 有概率悟性大幅提升", note: "cmd:shop:lucky_draw", emoji: "🎲" },
    { id: "vip_gym", name: "健身房年卡", summary: "¥1800 · 精力上限体验提升 · 有概率悟性+0.1 · P6 推荐", note: "cmd:shop:vip_gym", emoji: "🏋️" },
  ];

  const ACADEMY_COURSES_UI = [
    { id: "base", name: "基础进阶课", summary: "¥100 · 精力 -30 · 有概率悟性+0.05 · 综合向上", emoji: "📘" },
    { id: "hard_camp", name: "硬核技术训练营", summary: "¥200 · 精力 -40 · 硬技能 +4 · 高概率悟性+0.1", emoji: "🧪" },
    { id: "soft_workshop", name: "沟通协作工作坊", summary: "¥200 · 精力 -30 · 软技能 +4 · 高概率悟性+0.1", emoji: "🗣️" },
    { id: "leadership", name: "项目管理与领导力", summary: "¥300 · 精力 -35 · 软技能 +2 · 政治资本提升 · 悟性小幅提升 · P6 推荐", emoji: "👑" },
    { id: "architecture", name: "系统架构设计实战", summary: "¥280 · 精力 -35 · 硬技能 +3 · 软技能 +1 · 悟性+0.15 概率提升 · P6 推荐", emoji: "🏗️" },
    { id: "performance", name: "性能优化与压测", summary: "¥260 · 精力 -35 · 硬技能 +3 · 悟性+0.1 概率提升", emoji: "⚙️" },
    { id: "product_sense", name: "产品感与体验设计", summary: "¥220 · 精力 -30 · 软技能 +3 · 悟性+0.1 概率提升", emoji: "🎯" },
    { id: "data_analysis", name: "数据分析与指标体系", summary: "¥240 · 精力 -30 · 硬技能 +2 · 软技能 +1 · 悟性+0.1 概率提升", emoji: "📊" },
    { id: "negotiation", name: "跨部门协同与谈判", summary: "¥260 · 精力 -35 · 软技能 +3 · 悟性+0.1 概率提升 · P6 推荐", emoji: "🤝" },
    { id: "review_skill", name: "复盘与总结能力", summary: "¥180 · 精力 -25 · 硬技能 +1 · 软技能 +2 · 高概率悟性+0.1", emoji: "📝" },
    { id: "writing", name: "文档与写作训练", summary: "¥160 · 精力 -20 · 硬/软技能小幅提升 · 悟性+0.05 概率提升", emoji: "✍️" },
    { id: "ai_course", name: "AI 应用实践营", summary: "¥320 · 精力 -40 · 硬技能 +3 · 软技能 +1 · 必定悟性+0.2 · P6 推荐", emoji: "🤖" },
    { id: "mentor_clinic", name: "导师一对一诊室", summary: "¥260 · 精力 -25 · 硬技能 +1 · 软技能 +2 · 高概率悟性+0.15 · 限购 · P6 推荐", emoji: "🧑‍🏫" },
    { id: "presentation", name: "演讲与汇报训练营", summary: "¥230 · 精力 -30 · 软技能 +3 · 高概率悟性+0.1", emoji: "🎤" },
    { id: "team_building", name: "带团队实战营", summary: "¥340 · 精力 -40 · 软技能 +3 · 硬技能 +1 · 必定悟性+0.15 · P7 推荐", emoji: "🧑‍💼" },
    { id: "career_design", name: "职业路径设计课", summary: "¥220 · 精力 -25 · 软技能 +2 · 高概率悟性+0.1", emoji: "🧭" },
    { id: "startup_mind", name: "创业思维与商业模型", summary: "¥260 · 精力 -35 · 硬/软技能 +2 · 必定悟性+0.15 · P6 推荐", emoji: "🚀" },
    { id: "game_design", name: "游戏策划与数值设计", summary: "¥260 · 精力 -35 · 硬技能 +2 · 软技能 +1 · 悟性+0.1 概率提升", emoji: "🎮" },
    { id: "ops_system", name: "运营体系与活动设计", summary: "¥220 · 精力 -30 · 硬技能 +1 · 软技能 +2 · 悟性+0.1 概率提升", emoji: "📈" },
    { id: "random_inspiration", name: "灵感涌现工作坊", summary: "¥200 · 精力 -25 · 硬/软技能小幅提升 · 有概率悟性+0.2 爆发", emoji: "💡" },
  ];

  const WorkbenchItemCard = ({ item, type, onAction }) => {
    const badges = [];
    if (item.summary.includes("限购")) badges.push("限购");
    if (item.summary.includes("P6")) badges.push("P6");
    if (item.summary.includes("P7")) badges.push("P7");
    if (
      item.summary.includes("必定悟性") ||
      item.summary.includes("高概率悟性") ||
      item.summary.includes("悟性+0.2")
    ) {
      badges.push("悟性加成");
    }

    const actionText =
      type === "academy" ? "报名" : type === "rice" ? "点这份" : "购买";

    const buttonBase =
      type === "rice"
        ? "bg-orange-500 hover:bg-orange-600"
        : type === "academy"
        ? "bg-purple-500 hover:bg-purple-600"
        : "bg-blue-500 hover:bg-blue-600";

    return (
      <div className="border border-gray-200 rounded-xl p-3 flex flex-col justify-between bg-gradient-to-br from-gray-50 to-white hover:from-white hover:to-gray-50 hover:shadow-md transition-transform hover:-translate-y-0.5">
        <div className="flex items-center mb-2">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center text-2xl bg-gray-100 mr-3">
            {item.emoji}
          </div>
          <div className="flex-1">
            <div className="text-sm font-bold text-gray-900 truncate">
              {item.name}
            </div>
            {badges.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1">
                {badges.map((b) => (
                  <span
                    key={b}
                    className="px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-yellow-100 text-yellow-700"
                  >
                    {b}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
        <p className="text-xs text-gray-600 font-mono mb-2 line-clamp-3">
          {item.summary}
        </p>
        <button
          onClick={() => onAction(`${type}:${item.id}`)}
          className={`mt-auto w-full py-1.5 text-xs font-medium text-white rounded-lg ${buttonBase}`}
        >
          {actionText}
        </button>
      </div>
    );
  };

  const WorkbenchSection = ({ title, description, type, icon, items, onAction }) => {
    const iconClasses =
      type === "rice"
        ? "bg-orange-100 text-orange-600"
        : type === "academy"
        ? "bg-purple-100 text-purple-600"
        : "bg-blue-100 text-blue-600";

    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div
          className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${iconClasses}`}
        >
          {icon}
        </div>
        <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-sm text-gray-500 mb-4">{description}</p>
        <div className="grid grid-cols-1 gap-3 max-h-80 overflow-y-auto pr-1">
          {items.map((item) => (
            <WorkbenchItemCard
              key={item.id}
              item={item}
              type={type}
              onAction={onAction}
            />
          ))}
        </div>
      </div>
    );
  };

  if (isOnboarding) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 font-sans p-6">
        <div className="bg-white p-10 rounded-2xl shadow-2xl w-full max-w-4xl flex flex-col md:flex-row gap-10">
          
          {/* Left Side: Intro */}
          <div className="md:w-1/3 flex flex-col justify-center border-r border-gray-100 pr-6">
            <div className="mb-6 text-center md:text-left">
               <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mb-4 mx-auto md:mx-0 shadow-lg transform rotate-3">
                  <span className="text-white font-bold text-2xl">M</span>
               </div>
               <h1 className="text-3xl font-extrabold text-gray-900 mb-2">Tech Otakus Save The World</h1>
               <p className="text-gray-500 text-sm">欢迎加入米哈游！请完善你的入职信息，开始你的冒险。</p>
            </div>
            
            <div className="space-y-4">
              <label className="block text-sm font-bold text-gray-700">你的名字</label>
              <input 
                type="text" 
                className="block w-full rounded-xl border-gray-200 bg-gray-50 shadow-sm p-3 border focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
                value={onboardData.name}
                onChange={e => setOnboardData({...onboardData, name: e.target.value})}
                placeholder="旅行者"
              />
            </div>
            
             <button 
              onClick={handleOnboard}
              disabled={!onboardData.name || loading}
              className={`mt-8 w-full py-3 px-6 rounded-xl shadow-lg transform transition-all flex items-center justify-center gap-2 font-bold text-lg
                ${onboardData.name && !loading ? 'bg-blue-600 text-white hover:bg-blue-700 hover:scale-105' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
            >
              {loading ? "正在办理..." : "办理入职"} <Send className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>

          {/* Right Side: Selection */}
          <div className="md:w-2/3 space-y-8">
            
            {/* Role Selection */}
            <div>
              <h3 className="text-lg font-bold text-gray-800 mb-4">
                选择岗位
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {ROLES.map(role => (
                  <div 
                    key={role.id}
                    onClick={() => setOnboardData({...onboardData, role: role.id})}
                    className={`cursor-pointer p-4 rounded-xl border-2 transition-all duration-200 flex flex-col items-center text-center gap-2
                      ${onboardData.role === role.id ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' : 'border-gray-100 bg-white hover:border-gray-300 hover:shadow-md'}`}
                  >
                    <div className={`p-3 rounded-full ${onboardData.role === role.id ? 'bg-blue-200 text-blue-700' : 'bg-gray-100 text-gray-500'}`}>
                      {role.icon}
                    </div>
                    <div>
                      <div className="font-bold text-gray-900">{role.name}</div>
                      <div className="text-xs text-gray-500 mt-1">{role.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Project Selection */}
            <div>
              <h3 className="text-lg font-bold text-gray-800 mb-4">
                意向项目组
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {PROJECTS.map(proj => (
                  <div 
                    key={proj.id}
                    onClick={() => setOnboardData({...onboardData, project_name: proj.id})}
                    className={`cursor-pointer p-4 rounded-xl border-2 transition-all duration-200 relative overflow-hidden
                      ${onboardData.project_name === proj.id ? 'border-purple-500 bg-purple-50 ring-2 ring-purple-200' : 'border-gray-100 bg-white hover:border-gray-300 hover:shadow-md'}`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-bold text-gray-900">{proj.name}</span>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium 
                        ${proj.status === 'Live' ? 'bg-green-100 text-green-700' : 
                          'bg-orange-100 text-orange-700'}`}>
                {proj.statusCN}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mb-2">{proj.desc}</div>
                    <div className="text-xs font-mono text-gray-400 bg-gray-100 inline-block px-2 py-0.5 rounded">风险：{proj.risk}</div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>
    );
  }

  if (!gameState) return <div className="flex h-screen items-center justify-center">Loading...</div>;

  const { player } = gameState;
  const currentProject = gameState?.projects?.[player.current_project];
  const projectDisplayName = mapProjectToCN(player.current_project);
  const computeRevenueTarget = (p) => {
    if (!p) return 0;
    let base = 50000;
    if (p.type === "Infra") base = 25000;
    else if (p.type === "App") base = 35000;
    return Math.floor(base * Math.max(1, p.difficulty));
  };
  const dayLabels = {
    1: "周一",
    2: "周二",
    3: "周三",
    4: "周四",
    5: "周五",
    6: "周六",
    7: "周日",
  };

  const dynamicQuickReplies = gameState?.suggested_replies ? gameState.suggested_replies.slice(0, 2) : [];
  const fixedQuickReplies = ["爆肝干活", "摸鱼一会", "给大佬发消息", "汇报下进度"];
  const fixedQuickReplyCommandMap = {
    "爆肝干活": "work_hard",
    "摸鱼一会": "rest",
    "给大佬发消息": "msg_boss",
    "汇报下进度": "report",
  };
  const inputDisabled = gameState.game_over || !!gameState.active_global_event || isTyping;

  const selectedBackendNpc = selectedChat !== 'group' ? gameState?.npcs?.[selectedChat] : null;

  return (
    <div className="flex h-screen bg-white overflow-hidden font-sans relative">
    
      {/* Game Over Modal */}
      {gameState.game_over && (
         <div className="absolute inset-0 bg-black bg-opacity-70 z-[100] flex items-center justify-center backdrop-blur-sm">
            <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-md w-full text-center border-4 border-red-500 animate-bounce-slow">
               <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6 text-red-600 text-3xl font-bold">
                  !
               </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">游戏结束</h2>
               <p className="text-xl text-red-600 font-bold mb-6">
                 {{
                   Fired: "你被开除了！",
                   Exhausted: "你累倒了！",
                   Executive: "你成为高管！",
                   Rich: "你财富自由！",
                   Producer: "你成了金牌制作人！",
                   Stable: "你平稳度过一年",
                   Resignation: "你体面地递交了离职申请。",
                 }[gameState.ending] || "游戏结束"}
               </p>
               <p className="text-gray-600 mb-8">
                  {gameState.ending === "Fired" 
                    ? "由于信任度过低，你收到了HR的辞退通知。保安正在护送你离开园区..." 
                    : (gameState.ending === "Exhausted" ? "请注意休息，身体是革命的本钱。" : "你的职业生涯阶段性收官。")}
               </p>
               <button 
                  onClick={handleRestart}
                  className="bg-red-600 text-white px-8 py-3 rounded-xl hover:bg-red-700 transition font-bold text-lg w-full"
               >
                  重新开始
               </button>
            </div>
         </div>
      )}

      {gameState.active_global_event && !gameState.game_over && (
         <div className="absolute inset-0 bg-black bg-opacity-60 z-[90] flex items-center justify-center backdrop-blur-sm">
            <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-md w-full text-center border-2 border-blue-500">
               <h2 className="text-2xl font-bold text-gray-900 mb-4">{gameState.active_global_event.title}</h2>
               <p className="text-sm text-gray-700 mb-6 leading-relaxed">{gameState.active_global_event.description}</p>
               <button
                  onClick={async () => {
                    try {
                      const res = await axios.post(`${API_URL}/event/ack`);
                      setGameState(res.data);
                    } catch (err) {
                      console.error(err);
                    }
                  }}
                  className="bg-blue-600 text-white px-8 py-2 rounded-lg hover:bg-blue-700 transition font-medium text-sm w-full"
               >
                  知道了，继续上班
               </button>
            </div>
         </div>
      )}

      {/* 1. App Sidebar (Narrow Left) */}
      <div className="w-16 bg-gray-100 border-r border-gray-200 flex flex-col items-center py-4 space-y-6">
        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-xl shadow-sm">
          M
        </div>
        <div className="flex flex-col space-y-4 w-full items-center">
          <button 
             onClick={() => setCurrentView('chat')}
             className={`p-2 rounded-lg transition ${currentView === 'chat' ? 'text-blue-600 bg-blue-100' : 'text-gray-500 hover:bg-gray-200'}`}
          >
             <MessageSquare className="w-6 h-6"/>
          </button>
          <button 
             onClick={() => setCurrentView('workbench')}
             className={`p-2 rounded-lg transition ${currentView === 'workbench' ? 'text-blue-600 bg-blue-100' : 'text-gray-500 hover:bg-gray-200'}`}
          >
             <Briefcase className="w-6 h-6"/>
          </button>
        </div>
      </div>

      {/* 2. List Sidebar (Chat List) - Only visible in Chat View */}
      {currentView === 'chat' && (
      <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="font-bold text-gray-800">消息</h2>
        </div>
        
        {/* Search */}
        <div className="px-3 py-2">
          <div className="relative">
            <input 
              type="text" 
              placeholder="搜索" 
              className="w-full bg-gray-200 text-sm rounded-md pl-8 pr-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              ref={searchInputRef}
            />
            <Search
              className="w-4 h-4 text-gray-400 absolute left-2 top-2 cursor-pointer"
              onClick={() => {
                if (searchInputRef.current) {
                  searchInputRef.current.focus();
                }
              }}
            />
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {/* Project Group */}
          <div 
            onClick={() => setSelectedChat('group')}
            className={`flex items-center px-3 py-3 cursor-pointer hover:bg-gray-200 ${selectedChat === 'group' ? 'bg-blue-100' : ''}`}
          >
            <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center text-white font-bold mr-3 flex-shrink-0">
              #{projectDisplayName ? projectDisplayName[0] : ''}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex justify-between items-baseline">
                <h3 className="text-sm font-medium text-gray-900 truncate">{projectDisplayName} 项目组</h3>
                <span className="text-xs text-gray-400">{getLastMsgTime('group', true)}</span>
              </div>
              <p className="text-xs text-gray-500 truncate">System: 欢迎新同学加入...</p>
            </div>
          </div>

          {/* NPCs */}
          {filteredNPCs.map(npc => (
            <div 
              key={npc.id}
              onClick={() => setSelectedChat(npc.id)}
              className={`flex items-center px-3 py-3 cursor-pointer hover:bg-gray-200 ${selectedChat === npc.id ? 'bg-blue-100' : ''}`}
            >
              <div className={`w-10 h-10 rounded-full ${npc.bg} flex items-center justify-center text-white font-bold mr-3 flex-shrink-0`}>
                {npc.avatar}
              </div>
              <div className="flex-1 min-w-0">
                 <div className="flex justify-between items-baseline">
                  <h3 className="text-sm font-medium text-gray-900 truncate">{npc.name}</h3>
                  <span className="text-xs text-gray-400">{getLastMsgTime(npc.id)}</span>
                </div>
                <p className="text-xs text-gray-500 truncate">
                  {(() => {
                    const backendNpc = gameState?.npcs?.[npc.id];
                    const baseInfo = backendNpc 
                      ? `${mapRoleToCN(backendNpc.role)} · ${backendNpc.level} · ${mapProjectToCN(backendNpc.project)}`
                      : mapRoleToCN(npc.role);
                    if (!gameState?.chat_history) return baseInfo;
                    const recent = gameState.chat_history.slice(-20);
                    const active = recent.some(msg => msg.sender === npc.name && msg.type === 'npc');
                    return baseInfo + (active ? " · 最近活跃" : " · 潜水中");
                  })()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
      )}

      {/* 3. Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-white relative">
        {/* Header */}
        <div className="h-16 border-b border-gray-200 flex justify-between items-center px-6">
          <div>
            <h2 className="text-lg font-bold text-gray-800">
               {currentView === 'chat' 
                  ? (selectedChat === 'group' ? `${projectDisplayName} 项目组` : npcList.find(n => n.id === selectedChat)?.name)
                  : '工作台'
               }
            </h2>
            {(currentView !== 'chat' || selectedChat === 'group') && (
            <p className="text-xs text-gray-500">
              第 {gameState.year || 1} 年 Q{gameState.quarter || 1} · 第 {gameState.week} 周
              {currentView === 'chat' && selectedChat === 'group' && currentProject ? ` · 风险 ${currentProject.risk}/100 · 士气 ${currentProject.morale}/100 · 信任 ${currentProject.stakeholder_trust}/100 · 进度 ${currentProject.progress}/100 · 营收 ¥${currentProject.revenue} · 营收目标 ¥${computeRevenueTarget(currentProject)}` : ""}
            </p>
            )}
            {currentView === 'chat' && selectedChat !== 'group' && (
              <p className="text-xs text-gray-500">
                {selectedBackendNpc 
                  ? `${mapRoleToCN(selectedBackendNpc.role)} · 职级 ${selectedBackendNpc.level} · 项目组 ${mapProjectToCN(selectedBackendNpc.project)}`
                  : ""}
              </p>
            )}
          </div>
          
          {/* Top Right: Personal Center Trigger */}
          <div className="flex items-center space-x-4">
             <div 
                className="flex items-center cursor-pointer hover:bg-gray-100 p-1 rounded-lg transition"
                onClick={() => setShowProfile(!showProfile)}
             >
                <div className="text-right mr-3 hidden md:block">
                  <p className="text-sm font-medium text-gray-900">{player.name}</p>
                  <p className="text-xs text-gray-500">P5 {mapRoleToCN(player.role)}</p>
                </div>
                <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold border border-blue-200">
                  {player.name[0]}
                </div>
             </div>
          </div>
        </div>

        {/* Profile Dropdown / Panel */}
        {showProfile && (
          <div className="absolute top-16 right-4 w-80 bg-white rounded-xl shadow-2xl border border-gray-200 z-50 p-6 animate-fade-in max-h-[80vh] overflow-y-auto">
             <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-800">个人中心</h3>
                <button onClick={() => setShowProfile(false)} className="text-gray-400 hover:text-gray-600">×</button>
             </div>
             
             <div className="space-y-6">
                {/* 1. 产出 */}
                <h4 className="text-xs text-gray-400 font-bold uppercase tracking-wider">产出</h4>
                <div className="grid grid-cols-2 gap-4">
                   <div className="bg-blue-50 p-3 rounded-lg text-center">
                      <p className="text-xs text-blue-500 uppercase font-bold">KPI</p>
                      <p className="text-2xl font-bold text-blue-700">{player.kpi}</p>
                   </div>
                   <div className="bg-yellow-50 p-3 rounded-lg text-center">
                      <p className="text-xs text-yellow-600 uppercase font-bold">金钱</p>
                      <p className="text-xl font-bold text-yellow-700">¥ {player.money}</p>
                   </div>
                   <div className="bg-purple-50 p-3 rounded-lg text-center">
                      <p className="text-xs text-purple-600 uppercase font-bold">政治资本</p>
                      <p className="text-xl font-bold text-purple-700">{player.political_capital}</p>
                   </div>
                   <div className="bg-gray-50 p-3 rounded-lg text-center">
                      <p className="text-xs text-gray-600 uppercase font-bold">等级</p>
                      <p className="text-xl font-bold text-gray-700">{player.level}</p>
                   </div>
                </div>

                {/* 2. 能力 */}
                <h4 className="text-xs text-gray-400 font-bold uppercase tracking-wider border-t border-gray-100 pt-4">能力</h4>
                <div className="space-y-3">
                   <div>
                      <div className="flex justify-between text-xs mb-1 font-medium text-gray-600">
                         <span>精力</span>
                         <span>{player.energy}/{player.max_energy}</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                         <div className="bg-green-500 h-2 rounded-full transition-all duration-500" style={{width: `${(player.energy/player.max_energy)*100}%`}}></div>
                      </div>
                   </div>
                   <div>
                      <div className="flex justify-between text-xs mb-1 font-medium text-gray-600">
                         <span>心情</span>
                         <span>{player.mood}/100</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                         <div className={`h-2 rounded-full transition-all duration-500 ${player.mood > 60 ? 'bg-yellow-400' : 'bg-red-500'}`} style={{width: `${player.mood}%`}}></div>
                      </div>
                   </div>
                   <div className="grid grid-cols-2 gap-2 mt-2">
                      <div className="flex justify-between text-sm bg-gray-50 p-2 rounded">
                         <span className="text-gray-600">硬技能</span>
                         <span className="font-mono font-bold">{player.hard_skill}</span>
                      </div>
                      <div className="flex justify-between text-sm bg-gray-50 p-2 rounded">
                         <span className="text-gray-600">软技能</span>
                         <span className="font-mono font-bold">{player.soft_skill}</span>
                      </div>
                   </div>
                   <div className="mt-2 space-y-1 text-xs text-gray-500">
                      <div>显卡等级：Lv{player.gear_gpu_level}</div>
                      <div>显示器等级：Lv{player.gear_monitor_level}</div>
                      <div>工位椅子等级：Lv{player.gear_chair_level}</div>
                   </div>
                </div>

                {/* 3. 元属性 */}
                <h4 className="text-xs text-gray-400 font-bold uppercase tracking-wider border-t border-gray-100 pt-4">元属性</h4>
                <div className="flex justify-between text-sm">
                   <span className="text-gray-500">悟性倍率</span>
                   <span className="font-mono">{player.learning_rate.toFixed(1)}x</span>
                </div>
             </div>
          </div>
        )}

        {currentView === 'workbench' && (
           <div className="flex-1 overflow-y-auto p-8 bg-gray-50">
              <div className="max-w-4xl mx-auto space-y-6">
               

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 <div
                  className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer"
                  onClick={() => setShowRice(true)}
                >
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 mb-4">
                       <Coffee className="w-6 h-6"/>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米饭 · 干饭时间</h3>
                    <p className="text-sm text-gray-500 mb-4">根据钱包、时间与职级选择不同档位的干饭方案。</p>
                  <button 
                    onClick={() => setShowRice(true)}
                    className="w-full py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium"
                  >
                    打开米饭
                  </button>
                 </div>

                 <div
                   className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer"
                   onClick={() => setShowShop(true)}
                 >
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mb-4">
                       <ShoppingBag className="w-6 h-6"/>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米购商城</h3>
                    <p className="text-sm text-gray-500 mb-4">购买礼物与固定商品升级，打造最强工位。</p>
                    <button 
                       onClick={() => setShowShop(true)}
                       className="w-full py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium"
                    >
                       打开米购
                    </button>
                 </div>

                 <div
                   className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer"
                   onClick={() => setShowAcademy(true)}
                 >
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                       <Briefcase className="w-6 h-6"/>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米忽悠学院</h3>
                    <p className="text-sm text-gray-500 mb-4">多种课程选择，定向提升硬技能、软技能与管理力。</p>
                    <button 
                       onClick={() => setShowAcademy(true)}
                       className="w-full py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 font-medium"
                    >
                       打开课程
                    </button>
                 </div>
                </div>
              </div>

              {showShop && (
                <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
                  <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6 relative">
                    <button onClick={() => setShowShop(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl">×</button>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米购商城</h3>
                    <div className="space-y-2 text-sm text-gray-500 mb-4">
                      <div className="font-mono">当前余额：¥ {player.money} · 精力：{player.energy}/{player.max_energy}</div>
                      <div>在这里可以购买礼物与固定商品升级，让你的工作效率和体验全面提升。</div>
                    </div>
                    {(() => {
                      const list = gameState?.workbench_feedback || [];
                      const last = [...list].reverse().find(f => f?.source === 'shop');
                      if (!last) return null;
                      return (
                        <div className="mb-4 p-3 rounded-lg border border-green-200 bg-green-50 text-xs text-green-700">
                          {last.content}
                        </div>
                      );
                    })()}
                    <div className="max-h-[60vh] overflow-y-auto">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {SHOP_ITEMS_UI.map((item) => (
                          <WorkbenchItemCard
                            key={item.id}
                            item={item}
                            type="shop"
                            onAction={sendWorkbenchCommand}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {showAcademy && (
                <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
                  <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6 relative">
                    <button onClick={() => setShowAcademy(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl">×</button>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米忽悠学院课程</h3>
                    <div className="space-y-2 text-sm text-gray-500 mb-4">
                      <div className="font-mono">当前余额：¥ {player.money} · 精力：{player.energy}/{player.max_energy}</div>
                      <div>选择不同课程，定向培养你的职业成长方向。</div>
                    </div>
                    {(() => {
                      const list = gameState?.workbench_feedback || [];
                      const last = [...list].reverse().find(f => f?.source === 'academy');
                      if (!last) return null;
                      return (
                        <div className="mb-4 p-3 rounded-lg border border-purple-200 bg-purple-50 text-xs text-purple-700">
                          {last.content}
                        </div>
                      );
                    })()}
                    <div className="max-h-[60vh] overflow-y-auto">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {ACADEMY_COURSES_UI.map((course) => (
                          <WorkbenchItemCard
                            key={course.id}
                            item={course}
                            type="academy"
                            onAction={sendWorkbenchCommand}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {showRice && (
                <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
                  <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6 relative">
                    <button onClick={() => setShowRice(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl">×</button>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米饭 · 干饭时间</h3>
                    <div className="space-y-2 text-sm text-gray-500 mb-4">
                      <div className="font-mono">当前余额：¥ {player.money} · 精力：{player.energy}/{player.max_energy}</div>
                      <div>根据钱包、时间与职级选择不同档位的干饭方案。</div>
                    </div>
                    {(() => {
                      const list = gameState?.workbench_feedback || [];
                      const last = [...list].reverse().find(f => f?.source === 'rice');
                      if (!last) return null;
                      return (
                        <div className="mb-4 p-3 rounded-lg border border-orange-200 bg-orange-50 text-xs text-orange-700">
                          {last.content}
                        </div>
                      );
                    })()}
                    <div className="max-h-[60vh] overflow-y-auto">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {RICE_OPTIONS.map((item) => (
                          <WorkbenchItemCard
                            key={item.id}
                            item={item}
                            type="rice"
                            onAction={sendWorkbenchCommand}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

           </div>
        )}

        {/* Chat Content */}
        {currentView === 'chat' && (
        <>
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
          {filteredMessages.map((msg, idx) => {
             return (
              <div
                key={idx}
                className={`flex ${msg.type === 'player' ? 'justify-end' : 'justify-start'}`}
                onContextMenu={(event) => handleMsgContextMenu(event, msg)}
              >
                {msg.type !== 'player' && msg.type !== 'system' && (
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center text-white text-xs mr-3 flex-shrink-0 ${
                    npcList.find(n => n.name.includes(msg.sender))?.bg || 'bg-gray-400'
                  }`}>
                    {msg.sender[0]}
                  </div>
                )}
                
                {msg.type === 'system' ? (
                  <div className="w-full flex justify-center my-2">
                    <span className="bg-gray-200 text-gray-500 text-xs px-4 py-1 rounded-full shadow-sm">
                      {msg.content}
                    </span>
                  </div>
                ) : (
                  <div className="max-w-[70%]">
                    {msg.type !== 'player' && (
                      <div className="flex items-baseline mb-1 ml-1">
                        <span className="text-xs font-bold text-gray-600 mr-2">{msg.sender}</span>
                        <span className="text-xs text-gray-400">{formatTime(msg.timestamp)}</span>
                      </div>
                    )}
                    <div className={`p-3 rounded-xl shadow-sm text-sm leading-relaxed ${
                      msg.type === 'player' 
                        ? 'bg-blue-100 text-gray-900 rounded-tr-none border border-blue-200' 
                        : 'bg-white text-gray-800 border border-gray-200 rounded-tl-none'
                    }`}>
                      {msg.content}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          
          {/* Typing Indicator */}
          {isTyping && (
             <div className="flex justify-start">
                <div className="w-9 h-9 rounded-full bg-gray-200 flex items-center justify-center text-gray-400 mr-3 animate-pulse">
                   ...
                </div>
                <div className="bg-gray-100 p-3 rounded-xl rounded-tl-none border border-gray-200">
                   <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                   </div>
                </div>
             </div>
          )}
          
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-gray-200">
          {!gameState.game_over && !gameState.active_global_event && (
            <div className="mb-2 flex flex-wrap gap-2">
              {dynamicQuickReplies.map((text, idx) => (
                <button
                  key={`dyn-${idx}`}
                  onClick={() => {
                    if (inputDisabled) return;
                    applyQuickReply(text);
                  }}
                  disabled={inputDisabled}
                  className={`px-3 py-1 rounded-full border border-gray-200 text-xs ${
                    inputDisabled
                      ? "bg-gray-50 text-gray-400 cursor-not-allowed"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {text}
                </button>
              ))}
              {fixedQuickReplies.map((text, idx) => {
                const cmd = fixedQuickReplyCommandMap[text];
                const handleClick = () => {
                  if (gameState?.game_over || gameState?.active_global_event || isTyping) return;
                  if (cmd) {
                    sendCommand(cmd);
                  } else {
                    applyQuickReply(text);
                  }
                };
                return (
                  <button
                    key={`fix-${idx}`}
                    onClick={handleClick}
                    disabled={gameState.game_over || !!gameState.active_global_event || isTyping}
                    className={`px-3 py-1 rounded-full border text-xs ${
                      gameState.game_over || !!gameState.active_global_event || isTyping
                        ? "border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed"
                        : "border-gray-100 bg-white text-gray-600 hover:bg-gray-100"
                    }`}
                  >
                    {text}
                  </button>
                );
              })}
            </div>
          )}
          <div className="flex space-x-3">
            <textarea
              disabled={inputDisabled}
              ref={inputRef}
              rows={2}
              className={`flex-1 bg-gray-100 border-0 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 text-sm resize-none ${inputDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
              placeholder={
                gameState.game_over
                  ? "游戏已结束"
                  : gameState.active_global_event
                  ? "全局事件进行中，请先阅读提示"
                  : `发送给 ${selectedChat === 'group' ? '项目组' : npcList.find(n => n.id === selectedChat)?.name}... (试着说: "帮我修个Bug" 或 "请你喝奶茶")`
              }
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.nativeEvent.isComposing) {
                  return;
                }
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
            />
            <button 
              onClick={sendMessage}
              disabled={inputDisabled || !input.trim()}
              className={`bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-medium text-sm flex items-center ${inputDisabled || !input.trim() ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              发送
            </button>
          </div>
        </div>
        </>
        )}
        {contextMenu.visible && (
          <div className="fixed inset-0 z-50" onClick={handleContextMenuClose}>
            <div
              className="absolute bg-white rounded-md shadow-lg border border-gray-200 py-1 text-sm"
              style={{ top: contextMenu.y, left: contextMenu.x }}
              onClick={e => e.stopPropagation()}
            >
              <button
                className="block w-full text-left px-4 py-1.5 hover:bg-gray-100 text-gray-700"
                onClick={handleContextMenuAt}
              >
                艾特ta
              </button>
              {contextMenu.msg?.content && (
                <button
                  className="block w-full text-left px-4 py-1.5 hover:bg-gray-100 text-gray-700"
                  onClick={handleContextMenuCopy}
                >
                  复制内容
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
