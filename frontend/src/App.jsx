import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, MessageSquare, Briefcase, ShoppingBag, Coffee, Search, Users, Home, LayoutDashboard, ArrowLeft } from 'lucide-react';

const MinimalBackpackIcon = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M6 9a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v9a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2Z"></path>
    <path d="M10 5h4"></path>
    <path d="M9 10h6"></path>
    <path d="M9 16h6"></path>
  </svg>
);

const API_URL = (import.meta.env.VITE_API_BASE_URL || "/api");

const SESSION_ID_KEY = "mh_session_id";
const getSessionId = () => {
  try {
    const existing = sessionStorage.getItem(SESSION_ID_KEY);
    if (existing) return existing;
    const sid = (globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`);
    sessionStorage.setItem(SESSION_ID_KEY, sid);
    return sid;
  } catch (e) {
    return "";
  }
};

const TUTORIAL_DONE_KEY = "mh_tutorial_v1_done";
const getTutorialDone = () => {
  try {
    return localStorage.getItem(TUTORIAL_DONE_KEY) === "1";
  } catch (e) {
    return false;
  }
};
const setTutorialDone = () => {
  try {
    localStorage.setItem(TUTORIAL_DONE_KEY, "1");
  } catch (e) {}
};

const mapRoleToCN = (role) => {
  if (!role) return "";
  const r = String(role);
  if (r === "Dev") return "研发";
  if (r === "Product") return "产品";
  if (r === "Ops") return "运营";
  if (r === "CTO") return "技术负责人";
  if (r === "CEO") return "总裁";
  if (r === "Art") return "美术";
  if (r === "HR") return "人力";
  if (r === "Brand") return "品牌";
  if (r === "Community") return "社群运营";
  if (r === "Data") return "数据";
  if (r === "Designer") return "策划";
  if (r === "QA") return "测试";
  if (r === "Animator") return "动画";
  if (r === "Audio") return "音频";
  if (r === "Lead") return "负责人";
  if (r === "OpsLead") return "运营负责人";
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

const ENDING_CONFIG = {
  Fired: {
    title: "你被开除了！",
    description: "由于信任度过低，你收到了HR的辞退通知。保安正在护送你离开园区...",
    condition: "高管信任 ≤ 0",
    type: "negative",
    icon: "🔴"
  },
  Exhausted: {
    title: "你累倒了！",
    description: "请注意休息，身体是革命的本钱。",
    condition: "精力 ≤ 0",
    type: "negative",
    icon: "💤"
  },
  Bankrupt: {
    title: "你破产了！",
    description: "存款归零，无法支付房租与基本开支，本局以破产结局收尾。",
    condition: "金钱 < 0",
    type: "negative",
    icon: "💸"
  },
  Depressed: {
    title: "你抑郁了！",
    description: "长期心情低落，医生建议你暂停工作进行治疗与休养。",
    condition: "心情 ≤ 0",
    type: "negative",
    icon: "😞"
  },
  Breakdown: {
    title: "你崩溃了！",
    description: "心情与精力长期低位，你在工位崩溃痛哭，选择离开。",
    condition: "心情 & 精力 长期低迷",
    type: "negative",
    icon: "💥"
  },
  Pip: {
    title: "你被 PIP 劝退！",
    description: "PIP 考核未通过，经理要求你离开团队并办理手续。",
    condition: "绩效考核不合格",
    type: "negative",
    icon: "📄"
  },
  ProjectCollapse: {
    title: "项目崩盘！",
    description: "项目彻底崩盘，你作为核心成员被迫背锅离场。",
    condition: "项目风险 ≥ 100",
    type: "negative",
    icon: "🧨"
  },
  ProjectCancelled: {
    title: "项目解散！",
    description: "资方取消项目组，你随团队一并解散并离开公司。",
    condition: "项目被砍",
    type: "negative",
    icon: "🛑"
  },
  Executive: {
    title: "你成为高管！",
    description: "你在组织里站稳了脚跟，成为了高管。",
    condition: "职级 ≥ P10",
    type: "positive",
    icon: "👑"
  },
  Rich: {
    title: "你财富自由！",
    description: "奖金与投资带来财富自由，你选择提前退休。",
    condition: "金钱 ≥ 1000万",
    type: "positive",
    icon: "💰"
  },
  Producer: {
    title: "你成了金牌制作人！",
    description: "你带队做出爆款，成为金牌制作人。",
    condition: "职级 ≥ P8 & 项目营收 ≥ 10万",
    type: "positive",
    icon: "🏆"
  },
  Stable: {
    title: "你被优化了",
    description: "刚刚到达35周岁你就被开除了。",
    condition: "存活满520周",
    type: "negative",
    icon: "👋"
  },
  Resignation: {
    title: "你体面地递交了离职申请。",
    description: "你体面地递交了离职申请。",
    condition: "主动辞职",
    type: "neutral",
    icon: "✉️"
  }
};

const getEndingConfig = (ending) => {
  return ENDING_CONFIG[ending] || {
    title: "游戏结束",
    description: "你的职业生涯阶段性收官。",
    condition: "未知条件",
    type: "negative",
    icon: "!"
  };
};

function App() {
  const [gameState, setGameState] = useState(null);
  const [npcList, setNpcList] = useState(NPC_LIST_FALLBACK);
  const [input, setInput] = useState("");
  const [onboardData, setOnboardData] = useState({ name: "", role: "Dev", project_name: "Genshin" });
  const [isOnboarding, setIsOnboarding] = useState(true);
  const [selectedChat, setSelectedChat] = useState('group'); // 'group' or NPC ID
  const [currentView, setCurrentView] = useState('chat'); // 'chat' or 'workbench' or 'profile'
  const [searchQuery, setSearchQuery] = useState("");
  const [showProfile, setShowProfile] = useState(false);
  const [showShop, setShowShop] = useState(false);
  const [showAcademy, setShowAcademy] = useState(false);
  const [showRice, setShowRice] = useState(false);
  const [showHouse, setShowHouse] = useState(false);
  const [loading, setLoading] = useState(false); // Global loading for onboard/commands
  const [isTyping, setIsTyping] = useState(false); // Chat stream typing indicator
  const [isQuickReplyLoading, setIsQuickReplyLoading] = useState(false);
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, msg: null });
  const [tutorialVisible, setTutorialVisible] = useState(false);
  const [tutorialStep, setTutorialStep] = useState(0);
  const [tutorialProgress, setTutorialProgress] = useState({
    firstMessage: false,
    firstCommand: false,
    firstRice: false,
  });
  const [tutorialFocusRect, setTutorialFocusRect] = useState(null);
  const [tutorialClaiming, setTutorialClaiming] = useState(false);
  const [profileTab, setProfileTab] = useState('bag'); // 'bag' or 'house'
  
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  const [mentionOpen, setMentionOpen] = useState(false);
  const [mentionQuery, setMentionQuery] = useState("");
  const [mentionIndex, setMentionIndex] = useState(0);
  const [mentionStart, setMentionStart] = useState(null);
  const searchInputRef = useRef(null);
  const tutorialInitRef = useRef(false);
  const quickCommandRef = useRef(null);
  const workbenchButtonRef = useRef(null);
  const riceCardRef = useRef(null);
  const riceModalRef = useRef(null);
  const [mobileChatOpen, setMobileChatOpen] = useState(false);

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

  useEffect(() => {
    if (isOnboarding) {
      tutorialInitRef.current = false;
      return;
    }
    if (!gameState) return;
    if (tutorialInitRef.current) return;
    tutorialInitRef.current = true;
    if (getTutorialDone()) return;
    setTutorialVisible(true);
    setTutorialStep(0);
    setTutorialProgress({
      firstMessage: false,
      firstCommand: false,
      firstRice: false,
    });
  }, [isOnboarding, gameState]);

  useEffect(() => {
    if (!tutorialVisible) return;
    if (tutorialStep === 1 && tutorialProgress.firstMessage) {
      setTutorialStep(2);
      return;
    }
    if (tutorialStep === 2 && tutorialProgress.firstCommand) {
      setTutorialStep(3);
      return;
    }
    if (tutorialStep === 3 && tutorialProgress.firstRice) {
      setTutorialStep(4);
      return;
    }
  }, [tutorialVisible, tutorialStep, tutorialProgress]);

  useEffect(() => {
    if (!tutorialVisible) return;
    if (tutorialStep !== 4) return;
    setShowRice(false);
    setShowShop(false);
    setShowAcademy(false);
    setShowProfile(false);
    setSelectedChat("group");
    setCurrentView("chat");
  }, [tutorialVisible, tutorialStep]);

  useEffect(() => {
    if (!tutorialVisible) return;
    if (tutorialStep === 1 || tutorialStep === 2) {
      if (currentView !== "chat") setCurrentView("chat");
    }
  }, [tutorialVisible, tutorialStep, currentView]);

  useEffect(() => {
    if (!tutorialVisible) {
      setTutorialFocusRect(null);
      return;
    }
    if (tutorialStep === 0 || tutorialStep === 4) {
      setTutorialFocusRect(null);
      return;
    }

    const pickEl = () => {
      if (tutorialStep === 1) return inputRef.current;
      if (tutorialStep === 2) return quickCommandRef.current;
      if (tutorialStep === 3) {
        if (currentView !== "workbench") return workbenchButtonRef.current;
        if (!showRice) return riceCardRef.current;
        return riceModalRef.current;
      }
      return null;
    };

    const update = () => {
      const el = pickEl();
      if (!el || typeof el.getBoundingClientRect !== "function") {
        setTutorialFocusRect(null);
        return;
      }
      if (typeof el.scrollIntoView === "function" && tutorialStep === 3 && currentView === "workbench" && !showRice) {
        el.scrollIntoView({ block: "center" });
      }
      const r = el.getBoundingClientRect();
      const pad = tutorialStep === 3 && showRice ? 12 : 10;
      const rect = {
        top: Math.max(8, r.top - pad),
        left: Math.max(8, r.left - pad),
        width: Math.max(0, r.width + pad * 2),
        height: Math.max(0, r.height + pad * 2),
      };
      setTutorialFocusRect(rect);
    };

    let raf1 = 0;
    let raf2 = 0;
    let t1 = 0;
    let t2 = 0;
    const schedule = () => {
      if (raf1) cancelAnimationFrame(raf1);
      if (raf2) cancelAnimationFrame(raf2);
      raf1 = requestAnimationFrame(() => {
        update();
        raf2 = requestAnimationFrame(update);
      });
      clearTimeout(t1);
      clearTimeout(t2);
      t1 = window.setTimeout(update, 50);
      t2 = window.setTimeout(update, 250);
    };

    schedule();
    const onResize = () => schedule();
    const onScroll = () => schedule();
    window.addEventListener("resize", onResize);
    window.addEventListener("scroll", onScroll, true);
    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("scroll", onScroll, true);
      if (raf1) cancelAnimationFrame(raf1);
      if (raf2) cancelAnimationFrame(raf2);
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [tutorialVisible, tutorialStep, currentView, showRice]);

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
      const res = await axios.post(`${API_URL}/init`, onboardData, {
        headers: { "X-Session-Id": getSessionId() },
      });
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
    if (tutorialVisible) {
      setTutorialProgress(prev => (prev.firstCommand ? prev : { ...prev, firstCommand: true }));
    }
    try {
      setIsTyping(true);
      const res = await axios.post(`${API_URL}/action`, { 
        action_type: "chat", 
        content: `cmd:${cmd}`,
        target_npc: "group"
      }, {
        headers: { "X-Session-Id": getSessionId() },
      });
      setGameState(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };
  
  const sendWorkbenchCommand = async (cmd) => {
    if (gameState?.game_over) return;
    if (tutorialVisible && String(cmd || "").startsWith("rice:")) {
      setTutorialProgress(prev => (prev.firstRice ? prev : { ...prev, firstRice: true }));
    }
    try {
      setIsTyping(true);
      const res = await axios.post(`${API_URL}/action`, {
        action_type: "workbench",
        content: `cmd:${cmd}`,
        target_npc: "workbench"
      }, {
        headers: { "X-Session-Id": getSessionId() },
      });
      setGameState(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || gameState?.game_over) return;
    const msg = input;
    const trimmed = String(msg || "").trim();
    if (tutorialVisible && trimmed && !trimmed.startsWith("cmd:")) {
      setTutorialProgress(prev => (prev.firstMessage ? prev : { ...prev, firstMessage: true }));
    }
    setInput("");
    setIsTyping(true); // Start typing indicator
    setIsQuickReplyLoading(true);
    
    // Optimistic append of player message so即使流式失败也能看到自己的发言
    setGameState(prevState => {
      if (!prevState) return prevState;
      const newState = { ...prevState };
      const history = Array.isArray(newState.chat_history) ? [...newState.chat_history] : [];
      const target = selectedChat === 'group' ? 'group' : selectedChat;
      const playerMsg = {
        sender: 'Me',
        content: msg,
        type: 'player',
        target,
        timestamp: new Date().toISOString(),
      };
      history.push(playerMsg);
      newState.chat_history = history;
      return newState;
    });
    
    try {
      const target = selectedChat === 'group' ? null : selectedChat;
      
      const response = await fetch(`${API_URL}/action/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Id': getSessionId(),
        },
        body: JSON.stringify({ 
          action_type: "chat", 
          content: msg,
          target_npc: target 
        })
      });

      if (!response.body) {
        throw new Error('No response body from stream endpoint');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let streamDone = false;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });

        while (true) {
          const boundaryIdx = buffer.indexOf("\n\n");
          if (boundaryIdx === -1) break;

          const rawEvent = buffer.slice(0, boundaryIdx);
          buffer = buffer.slice(boundaryIdx + 2);

          const dataLines = rawEvent
            .split("\n")
            .filter(l => l.startsWith("data:"))
            .map(l => l.slice(5).trimStart());

          if (dataLines.length === 0) continue;
          const dataStr = dataLines.join("\n").trim();
          if (!dataStr) continue;
          if (dataStr === "[DONE]") {
            streamDone = true;
            break;
          }

          try {
            const data = JSON.parse(dataStr);

            if (data.type === 'msg_append') {
              const incoming = data.msg;
              if (incoming && incoming.type && incoming.type !== 'player') {
                setIsTyping(false);
              }
            } else if (data.type === 'state_update') {
              setIsQuickReplyLoading(false);
              setIsTyping(false);
            }

            setGameState(prevState => {
              if (!prevState) return prevState;
              const newState = { ...prevState };

              if (data.type === 'msg_append') {
                const exists = (newState.chat_history || []).some(m =>
                  m.sender === data.msg.sender &&
                  m.content === data.msg.content &&
                  m.type === data.msg.type
                );
                if (!exists) {
                  newState.chat_history = [...newState.chat_history, data.msg];
                }
              } else if (data.type === 'msg_update') {
                const lastIdx = newState.chat_history.length - 1;
                if (lastIdx >= 0) {
                  newState.chat_history[lastIdx] = data.msg;
                  newState.chat_history = [...newState.chat_history];
                }
              } else if (data.type === 'state_update') {
                return data.state;
              } else if (data.type === 'error') {
                alert(data.content);
              }

              return newState;
            });
          } catch (e) {
            console.error("Parse error", e, dataStr);
          }
        }

        if (streamDone) break;
      }
    } catch (err) {
      console.error(err);
    } finally {
        setIsTyping(false);
        setIsQuickReplyLoading(false);
    }
  };

  const applyQuickReply = (text) => {
    if (!text || gameState?.game_over) return;
    setInput(text);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const mentionSuggestions = (() => {
    if (!mentionOpen) return [];
    const q = (mentionQuery || "").toLowerCase();
    const base = npcList || [];
    const list = q ? base.filter(n => (n.name || "").toLowerCase().includes(q)) : base.slice();
    return list.slice(0, 8);
  })();

  const insertMention = (name) => {
    const el = inputRef.current;
    const text = input || "";
    const pos = el ? el.selectionStart : text.length;
    const start = mentionStart ?? Math.max(0, text.lastIndexOf("@", pos));
    const left = text.slice(0, start);
    const right = text.slice(pos);
    const next = `${left}@${name} ${right}`;
    setInput(next);
    setMentionOpen(false);
    setMentionQuery("");
    setMentionIndex(0);
    setMentionStart(null);
    setTimeout(() => {
      if (inputRef.current) {
        const newPos = left.length + name.length + 2;
        inputRef.current.focus();
        inputRef.current.selectionStart = newPos;
        inputRef.current.selectionEnd = newPos;
      }
    }, 0);
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
    if (tutorialVisible) {
      setTutorialProgress(prev => (prev.firstMessage ? prev : { ...prev, firstMessage: true }));
    }
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
    const playerProjectId = gameState?.player?.current_project;

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
        project: gameState?.npcs?.[npc.id]?.project,
        lastTimestamp: last ? last.timestamp : null,
      };
    });

    if (!lowerQuery) {
      const projectNpcIds = new Set(
        withLast
          .filter(n => n.project && playerProjectId && n.project === playerProjectId)
          .map(n => n.id)
      );
      const base = withLast.filter(n => n.lastTimestamp || projectNpcIds.has(n.id));
      const allNoHistory = base.length > 0 && base.every(n => !n.lastTimestamp);
      if (allNoHistory) {
        return base.sort((a, b) => a.id.localeCompare(b.id));
      }
      return base.sort((a, b) => {
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
    { id: "Genshin", name: "原神", status: "Live", statusCN: "已上线", risk: 25, desc: "技术宅拯救世界" },
    { id: "Honkai3", name: "崩坏3", status: "Live", statusCN: "已上线", risk: 10, desc: "为世界上所有的美好而战" },
    { id: "HSR", name: "星穹铁道", status: "RD", statusCN: "预研", risk: 15, desc: "银河冒险之旅" },
    { id: "ZZZ", name: "绝区零", status: "RD", statusCN: "预研", risk: 20, desc: "潮流动作新游" },
    { id: "HYG", name: "神秘新作", status: "Pre", statusCN: "预研", risk: 30, desc: "神秘新作" },
    { id: "IAM", name: "iam", status: "Live", statusCN: "已上线", risk: 15, desc: "通行证与基础设施" },
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

  const HOUSE_ITEMS_UI = [
    { id: "rent_studio", name: "桂林路小单间", summary: "¥3000 · P5 解锁 · 每周疲劳 -2 · 桂林路步行通勤，夜宵丰富", note: "cmd:house:rent_studio", emoji: "🛏️" },
    { id: "old_apartment", name: "田林路一居", summary: "¥6000 · P5 解锁 · 每周疲劳 -3 · 田林路烟火气，小区生活踏实", note: "cmd:house:old_apartment", emoji: "🏠" },
    { id: "new_apartment", name: "徐家汇两居", summary: "¥12000 · P6 解锁 · 每周疲劳 -4 · 徐家汇通勤与生活品质升级", note: "cmd:house:new_apartment", emoji: "🏢" },
    { id: "city_center_loft", name: "黄浦区LOFT", summary: "¥20000 · P6 解锁 · 每周疲劳 -5 · 黄浦区夜景与海风，下班即 Citywalk", note: "cmd:house:city_center_loft", emoji: "🌃" },
    { id: "river_view_house", name: "外滩大平层", summary: "¥35000 · P7 解锁 · 每周疲劳 -6 · 外滩浦江江景，回家即度假", note: "cmd:house:river_view_house", emoji: "🌅" },
    { id: "villa", name: "佘山大别墅", summary: "¥50000 · P8 解锁 · 每周疲劳 -7 · 佘山山林躺平，远离喧嚣", note: "cmd:house:villa", emoji: "🌳" },
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

  const HOUSE_OWNED_META = [
    { id: "starter_rent", name: "滴水湖小单间", summary: "默认持有 · 每周疲劳 -1 · 滴水湖小单间", emoji: "🏚️" },
    ...HOUSE_ITEMS_UI,
  ];

  const WorkbenchItemCard = ({ item, type, onAction }) => {
    const badges = [];
    if (item.summary.includes("限购")) badges.push("限购");
    if (item.summary.includes("P5")) badges.push("P5");
    if (item.summary.includes("P6")) badges.push("P6");
    if (item.summary.includes("P7")) badges.push("P7");
    if (item.summary.includes("P8")) badges.push("P8");
    if (
      item.summary.includes("必定悟性") ||
      item.summary.includes("高概率悟性") ||
      item.summary.includes("悟性+0.2")
    ) {
      badges.push("悟性加成");
    }

    const actionText =
      type === "academy"
        ? "报名"
        : type === "rice"
        ? "点这份"
        : type === "house"
        ? "购入"
        : "购买";

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
        : type === "house"
        ? "bg-emerald-100 text-emerald-600"
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
              <div className="flex items-center justify-center md:justify-start mb-4 space-x-3">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto md:mx-0 shadow-lg transform rotate-3">
                  <span className="text-white font-bold text-2xl">M</span>
                </div>
                <div className="flex items-center gap-2">
                   <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-gray-100 text-gray-600 border border-gray-200">
                    v0.1.3
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-700 border border-purple-200">
                    内测
                  </span>
                </div>
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
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
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
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                    <div className="text-xs font-mono text-gray-400 bg-gray-100 inline-block px-2 py-0.5 rounded">风险：{proj.risk}/100</div>
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
  const fatigue = Math.max(0, Math.min(100, player.fatigue ?? 0));
  let fatigueColor = "bg-emerald-400";
  if (fatigue >= 70) {
    fatigueColor = "bg-red-500";
  } else if (fatigue >= 40) {
    fatigueColor = "bg-amber-400";
  }
  const ending = gameState.ending;
  const endingConfig = getEndingConfig(ending);
  const endingType = endingConfig.type;
  
  const modalBorder = endingType === "positive" ? "border-emerald-500" : (endingType === "neutral" ? "border-gray-400" : "border-red-500");
  const iconBg = endingType === "positive" ? "bg-emerald-100" : (endingType === "neutral" ? "bg-gray-100" : "bg-red-100");
  const iconText = endingType === "positive" ? "text-emerald-600" : (endingType === "neutral" ? "text-gray-600" : "text-red-600");
  const titleColor = endingType === "positive" ? "text-emerald-700" : (endingType === "neutral" ? "text-gray-800" : "text-red-600");
  const buttonColor = endingType === "positive" ? "bg-emerald-600 hover:bg-emerald-700" : (endingType === "neutral" ? "bg-gray-700 hover:bg-gray-800" : "bg-red-600 hover:bg-red-700");
  const iconChar = endingConfig.icon;
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
  const fixedQuickReplies = ["老实干活", "技术突破", "包装PPT", "拉群对齐", "向上管理", "带薪摸鱼"];
  const fixedQuickReplyCommandMap = {
    "老实干活": "work_normal",
    "技术突破": "tech_breakthrough",
    "包装PPT": "make_ppt",
    "拉群对齐": "align_meeting",
    "向上管理": "msg_boss",
    "带薪摸鱼": "paid_slack",
  };
  const inputDisabled = gameState.game_over || !!gameState.active_global_event || isTyping;

  const selectedBackendNpc = selectedChat !== 'group' ? gameState?.npcs?.[selectedChat] : null;

  return (
    <div className="flex h-screen bg-white overflow-hidden font-sans relative">
      {tutorialVisible && !gameState.game_over && !gameState.active_global_event && (
        <div className="fixed inset-0 z-[120] pointer-events-none">
          {tutorialStep === 0 || tutorialStep === 4 ? (
            <div className="absolute inset-0 bg-black/70 backdrop-blur-[1px] pointer-events-auto" />
          ) : tutorialFocusRect ? (
            <>
              <div
                className="absolute left-0 top-0 w-full bg-black/70 backdrop-blur-[1px] pointer-events-auto"
                style={{ height: `${tutorialFocusRect.top}px` }}
              />
              <div
                className="absolute left-0 bg-black/70 backdrop-blur-[1px] pointer-events-auto"
                style={{
                  top: `${tutorialFocusRect.top + tutorialFocusRect.height}px`,
                  height: `calc(100vh - ${tutorialFocusRect.top + tutorialFocusRect.height}px)`,
                  width: "100%",
                }}
              />
              <div
                className="absolute bg-black/70 backdrop-blur-[1px] pointer-events-auto"
                style={{
                  top: `${tutorialFocusRect.top}px`,
                  left: "0px",
                  width: `${tutorialFocusRect.left}px`,
                  height: `${tutorialFocusRect.height}px`,
                }}
              />
              <div
                className="absolute bg-black/70 backdrop-blur-[1px] pointer-events-auto"
                style={{
                  top: `${tutorialFocusRect.top}px`,
                  left: `${tutorialFocusRect.left + tutorialFocusRect.width}px`,
                  width: `calc(100vw - ${tutorialFocusRect.left + tutorialFocusRect.width}px)`,
                  height: `${tutorialFocusRect.height}px`,
                }}
              />
              <div
                className="absolute rounded-2xl ring-4 ring-white/90 pointer-events-none"
                style={{
                  top: `${tutorialFocusRect.top}px`,
                  left: `${tutorialFocusRect.left}px`,
                  width: `${tutorialFocusRect.width}px`,
                  height: `${tutorialFocusRect.height}px`,
                }}
              />
            </>
          ) : (
            <div className="absolute inset-0 bg-black/70 backdrop-blur-[1px] pointer-events-auto" />
          )}

          {tutorialStep === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center px-6 pointer-events-auto">
              <div className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-200">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-8 text-white">
                  <div className="text-2xl font-extrabold">欢迎加入米哈游</div>
                  <div className="mt-2 text-sm text-white/90">
                    用聊天与指令推动项目进度，在有限精力内做出最优选择。
                  </div>
                </div>
                <div className="p-8">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="rounded-2xl border border-gray-200 p-5 bg-gradient-to-br from-gray-50 to-white">
                      <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center mb-3">
                        <MessageSquare className="w-5 h-5" />
                      </div>
                      <div className="font-bold text-gray-900">消息模式</div>
                      <div className="text-sm text-gray-600 mt-1">
                        在项目群聊/私聊里沟通、推进与博弈。
                      </div>
                    </div>
                    <div className="rounded-2xl border border-gray-200 p-5 bg-gradient-to-br from-gray-50 to-white">
                      <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center mb-3">
                        <Briefcase className="w-5 h-5" />
                      </div>
                      <div className="font-bold text-gray-900">工作台</div>
                      <div className="text-sm text-gray-600 mt-1">
                        米购/学院/米饭补给，强化能力与续航。
                      </div>
                    </div>
                    <div className="rounded-2xl border border-gray-200 p-5 bg-gradient-to-br from-gray-50 to-white">
                      <div className="w-10 h-10 rounded-xl bg-orange-100 text-orange-700 flex items-center justify-center mb-3">
                        <Coffee className="w-5 h-5" />
                      </div>
                      <div className="font-bold text-gray-900">资源管理</div>
                      <div className="text-sm text-gray-600 mt-1">
                        精力/心情/余额与项目指标会共同决定结局。
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 flex items-center justify-between">
                    <div className="text-xs text-gray-500">
                      1/4 · 大约 30 秒完成
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setTutorialDone();
                          setTutorialVisible(false);
                        }}
                        className="px-4 py-2 rounded-xl text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
                      >
                        跳过
                      </button>
                      <button
                        onClick={() => setTutorialStep(1)}
                        className="px-4 py-2 rounded-xl text-sm font-bold bg-blue-600 text-white hover:bg-blue-700"
                      >
                        开始引导
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : tutorialStep === 4 ? (
            <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-[min(720px,calc(100vw-32px))] pointer-events-auto">
              <div className="w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-200 mx-auto">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-7 text-white">
                  <div className="text-2xl font-extrabold">恭喜你完成新手任务</div>
                  <div className="mt-2 text-sm text-white/90">
                    你已经掌握了聊天、命令与补给的基本操作。
                  </div>
                </div>
                <div className="p-8">
                  <div className="rounded-2xl border border-blue-200 bg-blue-50 p-5">
                    <div className="text-sm font-bold text-blue-900">新手奖励</div>
                    <div className="mt-2 text-sm text-blue-800">
                      金钱 +200 · 精力 +10 · 心情 +5
                    </div>
                    <div className="mt-1 text-xs text-blue-700/80">
                      精力与心情会自动按上限处理。
                    </div>
                  </div>

                  <div className="mt-6 flex items-center justify-between gap-3">
                    <button
                      onClick={() => {
                        setTutorialDone();
                        setTutorialVisible(false);
                      }}
                      className="px-4 py-2 rounded-xl text-sm font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
                    >
                      稍后再说
                    </button>
                    <button
                      onClick={async () => {
                        if (tutorialClaiming) return;
                        setTutorialClaiming(true);
                        try {
                          const res = await axios.post(
                            `${API_URL}/action`,
                            {
                              action_type: "chat",
                              content: "cmd:tutorial_reward",
                              target_npc: "group",
                            },
                            { headers: { "X-Session-Id": getSessionId() } }
                          );
                          setGameState(res.data);
                          setTutorialDone();
                          setTutorialVisible(false);
                        } catch (e) {
                        } finally {
                          setTutorialClaiming(false);
                        }
                      }}
                      className={`px-4 py-2 rounded-xl text-sm font-bold ${
                        tutorialClaiming
                          ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                          : "bg-blue-600 text-white hover:bg-blue-700"
                      }`}
                    >
                      领取奖励并回到聊天
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div
              className={`absolute ${
                tutorialStep === 3 ? "bottom-6" : "top-6"
              } left-1/2 -translate-x-1/2 w-[min(720px,calc(100vw-32px))] pointer-events-auto`}
            >
              <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-200">
                <div className="px-8 py-7 flex items-start justify-between gap-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                  <div>
                    <div className="text-sm font-bold">
                      {tutorialStep === 1
                        ? "发出第一句话"
                        : tutorialStep === 2
                        ? "触发第一次默认命令"
                        : "购买第一份米饭"}
                    </div>
                    <div className="text-xs text-white/80 mt-1">
                      {tutorialStep + 1}/4
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setTutorialDone();
                      setTutorialVisible(false);
                    }}
                    className="text-xs text-white/90 hover:text-white"
                  >
                    跳过
                  </button>
                </div>

                <div className="p-8">
                  {tutorialStep === 1 && (
                    <div className="text-sm text-gray-700 leading-relaxed">
                      在聊天区打一句话，开始你的工作吧！你也可以在消息区右键某位同事的消息，选择「艾特ta」，指定与他进行沟通。
                    </div>
                  )}
                  {tutorialStep === 2 && (
                    <div className="text-sm text-gray-700 leading-relaxed">
                      点一下快捷指令「老实干活」即可（会直接执行一条命令）。
                    </div>
                  )}
                  {tutorialStep === 3 && (
                    <div className="text-sm text-gray-700 leading-relaxed">
                      进入工作台 → 打开「米饭」→ 点任意一份完成首次购买。
                    </div>
                  )}

                  <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                    <div className={`rounded-xl border px-3 py-2 flex items-center justify-between ${tutorialProgress.firstMessage ? "border-blue-200 bg-blue-50 text-blue-700" : "border-gray-200 bg-gray-50 text-gray-600"}`}>
                      <span>第一句话</span>
                      <span>{tutorialProgress.firstMessage ? "已完成" : "未完成"}</span>
                    </div>
                    <div className={`rounded-xl border px-3 py-2 flex items-center justify-between ${tutorialProgress.firstCommand ? "border-blue-200 bg-blue-50 text-blue-700" : "border-gray-200 bg-gray-50 text-gray-600"}`}>
                      <span>第一次命令</span>
                      <span>{tutorialProgress.firstCommand ? "已完成" : "未完成"}</span>
                    </div>
                    <div className={`rounded-xl border px-3 py-2 flex items-center justify-between ${tutorialProgress.firstRice ? "border-blue-200 bg-blue-50 text-blue-700" : "border-gray-200 bg-gray-50 text-gray-600"}`}>
                      <span>第一次米饭</span>
                      <span>{tutorialProgress.firstRice ? "已完成" : "未完成"}</span>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      {tutorialStep === 1 && (
                        <button
                          onClick={() => inputRef.current?.focus?.()}
                          className="px-3 py-2 rounded-xl text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
                        >
                          聚焦输入框
                        </button>
                      )}
                      {tutorialStep === 3 && (
                        <button
                          onClick={() => {
                            setCurrentView("workbench");
                            setShowRice(true);
                          }}
                          className="px-3 py-2 rounded-xl text-xs font-medium bg-purple-100 text-purple-700 hover:bg-purple-200"
                        >
                          带我去米饭
                        </button>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setTutorialStep(0)}
                        className="px-3 py-2 rounded-xl text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
                      >
                        回看玩法
                      </button>
                      {tutorialStep === 1 && (
                        <button
                          onClick={() => setTutorialStep(2)}
                          disabled={!tutorialProgress.firstMessage}
                          className={`px-4 py-2 rounded-xl text-xs font-bold ${
                            tutorialProgress.firstMessage
                              ? "bg-blue-600 text-white hover:bg-blue-700"
                              : "bg-gray-200 text-gray-400 cursor-not-allowed"
                          }`}
                        >
                          下一步
                        </button>
                      )}
                      {tutorialStep === 2 && (
                        <button
                          onClick={() => setTutorialStep(3)}
                          disabled={!tutorialProgress.firstCommand}
                          className={`px-4 py-2 rounded-xl text-xs font-bold ${
                            tutorialProgress.firstCommand
                              ? "bg-blue-600 text-white hover:bg-blue-700"
                              : "bg-gray-200 text-gray-400 cursor-not-allowed"
                          }`}
                        >
                          下一步
                        </button>
                      )}
                      {tutorialStep === 3 && (
                        <button
                          onClick={() => {
                            setTutorialDone();
                            setTutorialVisible(false);
                          }}
                          disabled={!tutorialProgress.firstRice}
                          className={`px-4 py-2 rounded-xl text-xs font-bold ${
                            tutorialProgress.firstRice
                              ? "bg-blue-600 text-white hover:bg-blue-700"
                              : "bg-gray-200 text-gray-400 cursor-not-allowed"
                          }`}
                        >
                          完成引导
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    
      {/* Game Over Modal */}
      {gameState.game_over && (
         <div className="absolute inset-0 bg-black bg-opacity-70 z-[100] flex items-center justify-center backdrop-blur-sm">
            <div className={`bg-white p-8 rounded-2xl shadow-2xl max-w-md w-full text-center border-4 ${modalBorder} animate-bounce-slow`}>
               <div className={`w-20 h-20 ${iconBg} rounded-full flex items-center justify-center mx-auto mb-6 ${iconText} text-3xl font-bold`}>
                  {iconChar}
               </div>
              <h2 className={`text-3xl font-bold ${titleColor} mb-2`}>游戏结束</h2>
               <p className="text-xl text-red-600 font-bold mb-2">
                 {endingConfig.title}
               </p>
               <p className="text-sm text-gray-500 mb-6 font-mono bg-gray-50 py-1 px-3 rounded-lg inline-block">
                 触发条件：{endingConfig.condition}
               </p>
               <p className="text-gray-600 mb-8">
                  {endingConfig.description}
               </p>
               <button 
                  onClick={handleRestart}
                  className={`${buttonColor} text-white px-8 py-3 rounded-xl transition font-bold text-lg w-full`}
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
                      const res = await axios.post(`${API_URL}/event/ack`, null, {
                        headers: { "X-Session-Id": getSessionId() },
                      });
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
      <div className="hidden sm:flex w-16 md:w-20 bg-gray-100 border-r border-gray-200 flex-col items-center py-4 space-y-6">
        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-xl shadow-sm">
          M
        </div>
        <div className="flex flex-col space-y-4 w-full items-center">
          <button 
             onClick={() => setCurrentView('chat')}
             className={`p-3 rounded-lg transition ${currentView === 'chat' ? 'text-blue-600 bg-blue-100' : 'text-gray-500 hover:bg-gray-200'}`}
          >
             <MessageSquare className="w-6 h-6"/>
          </button>
          <button 
             onClick={() => setCurrentView('workbench')}
             ref={workbenchButtonRef}
             className={`p-3 rounded-lg transition ${currentView === 'workbench' ? 'text-blue-600 bg-blue-100' : 'text-gray-500 hover:bg-gray-200'}`}
          >
             <LayoutDashboard className="w-6 h-6"/>
          </button>
          <button 
             onClick={() => setCurrentView('profile')}
             className={`p-3 rounded-lg transition ${currentView === 'profile' ? 'text-blue-600 bg-blue-100' : 'text-gray-500 hover:bg-gray-200'}`}
          >
            <MinimalBackpackIcon className="w-7 h-7"/>
          </button>
        </div>
      </div>

      {/* 2. List Sidebar (Chat List) - Only visible in Chat View */}
      {currentView === 'chat' && (
      <div className="hidden sm:flex w-64 bg-gray-50 border-r border-gray-200 flex-col">
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
      <div className="flex-1 flex flex-col min-w-0 bg-white relative pb-16 sm:pb-0">
        {/* Header */}
        <div className="min-h-[3.5rem] sm:h-16 py-2 border-b border-gray-200 flex justify-between items-center px-3 sm:px-6">
          <div className="flex-1 min-w-0 mr-4">
            <div className="flex items-center gap-2">
              {currentView === 'chat' && (
                <button
                  className="sm:hidden p-2 -ml-2 rounded-lg text-gray-600 hover:bg-gray-100"
                  onClick={() => setMobileChatOpen(true)}
                >
                  <ArrowLeft className="w-5 h-5"/>
                </button>
              )}
              <h2 className="text-lg font-bold text-gray-800 truncate">
               {currentView === 'chat' 
                  ? (selectedChat === 'group' ? `${projectDisplayName} 项目组` : npcList.find(n => n.id === selectedChat)?.name)
                  : currentView === 'workbench'
                    ? '工作台'
                    : '我的'
               }
              </h2>
            </div>
            {(currentView !== 'chat' || selectedChat === 'group') && (
            <p className="text-[11px] sm:text-xs text-gray-500 break-words leading-tight mt-0.5">
              第 {gameState.year || 1} 年 Q{gameState.quarter || 1} · 第 {gameState.week} 周
              {currentView === 'chat' && selectedChat === 'group' && currentProject ? ` · 风险 ${currentProject.risk}/100 · 士气 ${currentProject.morale}/100 · 信任 ${currentProject.stakeholder_trust}/100 · 进度 ${currentProject.progress}/100 · 营收 ¥${currentProject.revenue} · 营收目标 ¥${computeRevenueTarget(currentProject)}` : ""}
            </p>
            )}
            {currentView === 'chat' && selectedChat !== 'group' && (
              <p className="text-[11px] sm:text-xs text-gray-500 break-words leading-tight mt-0.5">
                {selectedBackendNpc 
                  ? `${mapRoleToCN(selectedBackendNpc.role)} · 职级 ${selectedBackendNpc.level} · 项目组 ${mapProjectToCN(selectedBackendNpc.project)}`
                  : ""}
              </p>
            )}
          </div>
          
          {/* Top Right: Personal Center Trigger */}
          <div className="flex items-center space-x-4">
             <div className="hidden sm:flex items-center gap-2">
               <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gray-50 border border-gray-200">
                 <span className="w-2 h-2 rounded-full bg-blue-500" />
                 <span className="text-[10px] font-medium text-gray-500">精力</span>
                 <span className="text-xs font-mono font-bold text-gray-800">
                   {player.energy}/{player.max_energy}
                 </span>
               </div>
               <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gray-50 border border-gray-200">
                 <span className={`w-2 h-2 rounded-full ${player.mood > 60 ? "bg-purple-500" : "bg-red-500"}`} />
                 <span className="text-[10px] font-medium text-gray-500">心情</span>
                 <span className="text-xs font-mono font-bold text-gray-800">
                   {player.mood}/100
                 </span>
               </div>
             </div>
             {currentView === 'chat' && (
               <button
                 className="sm:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 hidden"
                 onClick={() => setMobileChatOpen(true)}
               >
                 <Users className="w-5 h-5"/>
               </button>
             )}
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
          <div
            className="fixed inset-0 z-40 flex justify-end items-start"
            onClick={() => setShowProfile(false)}
          >
            <div
              className="mt-16 mr-4 w-80 bg-white rounded-xl shadow-2xl border border-gray-200 p-6 animate-fade-in max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-800">个人中心</h3>
                <button
                  onClick={() => setShowProfile(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
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
                <h4 className="text-xs text-gray-400 font-bold uppercase tracking-wider border-t border-gray-100 pt-4">
                  能力
                </h4>
                <div className="space-y-3">
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
                </div>

                {/* 3. 元属性 */}
                <h4 className="text-xs text-gray-400 font-bold uppercase tracking-wider border-t border-gray-100 pt-4">
                  元属性
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">悟性倍率</span>
                    <span className="font-mono">{player.learning_rate.toFixed(1)}x</span>
                  </div>
                  <div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">疲劳值</span>
                      <span className="font-mono">{fatigue}/100</span>
                    </div>
                    <div className="mt-1 h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${fatigueColor}`}
                        style={{ width: `${fatigue}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'workbench' && (
           <div className="flex-1 overflow-y-auto p-8 bg-gray-50">
              <div className="max-w-4xl mx-auto space-y-6">
               

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                 <div
                  className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer"
                  onClick={() => setShowRice(true)}
                  ref={riceCardRef}
                >
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 mb-4">
                       <Coffee className="w-6 h-6"/>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米饭</h3>
                    <p className="text-sm text-gray-500 mb-4">根据钱包、时间与职级选择不同档位的干饭方案。</p>
                  <button 
                    onClick={() => setShowRice(true)}
                    className="w-full h-10 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium text-sm"
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
                       className="w-full h-10 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium text-sm"
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
                    <p className="text-sm text-gray-500 mb-4">多种课程选择，提升硬技能、软技能与管理力。</p>
                    <button 
                       onClick={() => setShowAcademy(true)}
                       className="w-full h-10 bg-purple-500 text-white rounded-lg hover:bg-purple-600 font-medium text-sm"
                    >
                       打开课程
                    </button>
                 </div>

                 <div
                   className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition cursor-pointer"
                   onClick={() => setShowHouse(true)}
                 >
                    <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center text-emerald-600 mb-4">
                       <Home className="w-6 h-6"/>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米哈房</h3>
                    <p className="text-sm text-gray-500 mb-4">购入不同档位房产，享受持续的疲劳减轻效果。</p>
                    <button 
                       onClick={() => setShowHouse(true)}
                       className="w-full h-10 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 font-medium text-sm"
                    >
                       打开米哈房
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
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
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
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
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
                  <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6 relative" ref={riceModalRef}>
                    <button onClick={() => setShowRice(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl">×</button>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米饭</h3>
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
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
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

              {showHouse && (
                <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-40">
                  <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-6 relative">
                    <button onClick={() => setShowHouse(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-xl">×</button>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">米哈房</h3>
                    <div className="space-y-2 text-sm text-gray-500 mb-4">
                      <div className="font-mono">当前余额：¥ {player.money} · 职级：{player.level}</div>
                      <div>每套房产仅可购入一次，购入后每周自动减轻一定疲劳值，档位越高效果越明显。</div>
                    </div>
                    {(() => {
                      const list = gameState?.workbench_feedback || [];
                      const last = [...list].reverse().find(f => f?.source === 'house');
                      if (!last) return null;
                      return (
                        <div className="mb-4 p-3 rounded-lg border border-emerald-200 bg-emerald-50 text-xs text-emerald-700">
                          {last.content}
                        </div>
                      );
                    })()}
                    <div className="max-h-[60vh] overflow-y-auto">
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
                        {HOUSE_ITEMS_UI.map((item) => (
                          <WorkbenchItemCard
                            key={item.id}
                            item={item}
                            type="house"
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

        {currentView === 'profile' && (
          <div className="flex-1 overflow-y-auto p-4 sm:p-8 bg-gray-50">
            <div className="max-w-4xl mx-auto space-y-6">
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-gray-800">我的</div>
                  <div className="text-xs text-gray-500 mt-1">查看已购道具、礼物与房产情况。</div>
                </div>
                <div className="inline-flex items-center bg-gray-100 rounded-full p-0.5 border border-gray-200">
                  <button
                    onClick={() => setProfileTab('bag')}
                    className={`px-3 py-1.5 text-xs rounded-full transition ${
                      profileTab === 'bag'
                        ? 'bg-white text-blue-700 shadow-sm'
                        : 'bg-transparent text-gray-600'
                    }`}
                  >
                    背包
                  </button>
                  <button
                    onClick={() => setProfileTab('house')}
                    className={`px-3 py-1.5 text-xs rounded-full transition ${
                      profileTab === 'house'
                        ? 'bg-white text-blue-700 shadow-sm'
                        : 'bg-transparent text-gray-600'
                    }`}
                  >
                    房产
                  </button>
                </div>
              </div>

              {profileTab === 'bag' && (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-sm font-semibold text-gray-800 mb-4">背包 · 道具与礼物</h3>
                  {(() => {
                    const purchases = gameState?.player?.workbench_purchases || {};
                    const shopEntries = Object.entries(purchases).filter(
                      ([key, count]) => key.startsWith('shop:') && count > 0
                    );
                    if (shopEntries.length === 0) {
                      return (
                        <p className="text-xs text-gray-500">
                          暂无已购道具或礼物。可以前往「工作台 - 米购商城」购买。
                        </p>
                      );
                    }
                    const uiMap = SHOP_ITEMS_UI.reduce((acc, item) => {
                      acc[item.id] = item;
                      return acc;
                    }, {});
                    return (
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
                        {shopEntries.map(([key, count]) => {
                          const [, itemId] = key.split(':');
                          const meta = uiMap[itemId] || {};
                          const isGift = itemId === 'gift';
                          const isGpu = itemId === 'gpu';
                          const isMonitor = itemId === 'monitor';
                          const isChair = itemId === 'chair';
                          let levelText = '';
                          if (isGpu) {
                            levelText = `显卡 Lv${player.gear_gpu_level}`;
                          } else if (isMonitor) {
                            levelText = `显示器 Lv${player.gear_monitor_level}`;
                          } else if (isChair) {
                            levelText = `工位椅 Lv${player.gear_chair_level}`;
                          }
                          return (
                            <div
                              key={key}
                              className="border border-gray-100 rounded-xl p-4 flex items-start gap-3 bg-gray-50"
                            >
                              <div className="w-9 h-9 rounded-lg bg-gray-100 flex items-center justify-center text-lg">
                                {meta.emoji || (isGift ? '🎁' : '🎒')}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between gap-2">
                                  <div className="flex items-center gap-2 min-w-0">
                                    <div className="text-sm font-medium text-gray-800 truncate">
                                      {meta.name || (isGift ? '礼物' : itemId)}
                                    </div>
                                    {levelText && (
                                      <span className="px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[10px] flex-shrink-0">
                                        {levelText}
                                      </span>
                                    )}
                                  </div>
                                  <div className="text-xs text-gray-500 flex-shrink-0">持有次数 ×{count}</div>
                                </div>
                                {meta.summary && (
                                  <div className="mt-1 text-xs text-gray-500 line-clamp-2">
                                    {meta.summary}
                                  </div>
                                )}
                                {isGift && (
                                  <div className="mt-1 text-[11px] text-pink-600">
                                    对应赠送玩法，可提升同事/老板信任。
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    );
                  })()}
                </div>
              )}

              {profileTab === 'house' && (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-sm font-semibold text-gray-800 mb-4">房产 · 已持有资产</h3>
                  {(() => {
                    const ownedIds = gameState?.player?.houses_owned || [];
                    const houseMap = HOUSE_OWNED_META.reduce((acc, item) => {
                      acc[item.id] = item;
                      return acc;
                    }, {});
                    const items = ownedIds.length
                      ? ownedIds.map(id => houseMap[id]).filter(Boolean)
                      : [];
                    if (items.length === 0) {
                      return (
                        <p className="text-xs text-gray-500">
                          暂无已持有房产。可以在「工作台 - 米哈房」中购入房产。
                        </p>
                      );
                    }
                    return (
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-4">
                        {items.map(item => (
                          <div
                            key={item.id}
                            className="border border-gray-100 rounded-xl p-4 flex items-start gap-3 bg-gray-50"
                          >
                            <div className="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center text-lg">
                              {item.emoji || '🏠'}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <div className="text-sm font-medium text-gray-800 truncate">
                                  {item.name}
                                </div>
                              </div>
                              {item.summary && (
                                <div className="mt-1 text-xs text-gray-500 line-clamp-2">
                                  {item.summary}
                                </div>
                              )}
                              {item.id === 'starter_rent' && (
                                <div className="mt-1 text-[11px] text-gray-500">
                                  上帝赐予你的奖励，提供轻微的每周疲劳减轻效果。
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    );
                  })()}
                </div>
              )}
            </div>
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
                    <span className="bg-gray-200 text-gray-600 text-xs px-4 py-1 rounded-full shadow-sm">
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
             <div className="flex justify-start items-center">
                <div className="w-9 h-9 rounded-full bg-gray-200 flex items-center justify-center text-gray-400 mr-3">
                   <div className="text-xs">?</div>
                </div>
                <div className="bg-gray-100 px-4 py-3 rounded-xl rounded-tl-none border border-gray-200 flex items-center space-x-2">
                   <span className="text-xs text-gray-500 font-medium">对方正在输入</span>
                   <div className="flex space-x-1">
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                   </div>
                </div>
             </div>
          )}
          
          <div ref={chatEndRef} />
        </div>

    {currentView === 'chat' && mobileChatOpen && (
      <div className="fixed inset-0 z-50 bg-white flex flex-col sm:hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between min-h-[3.5rem]">
          <h2 className="font-bold text-gray-800 text-lg">消息</h2>
        </div>
        <div className="px-3 py-2">
          <div className="relative">
            <input 
              type="text" 
              placeholder="搜索" 
              className="w-full bg-gray-100 text-sm rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          <div 
            onClick={() => { setSelectedChat('group'); setMobileChatOpen(false); }}
            className={`flex items-center px-4 py-4 cursor-pointer active:bg-gray-50 border-b border-gray-50 ${selectedChat === 'group' ? 'bg-blue-50' : ''}`}
          >
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold mr-4 flex-shrink-0 shadow-sm">
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
            {filteredNPCs.map(npc => (
              <div 
                key={npc.id}
                onClick={() => { setSelectedChat(npc.id); setMobileChatOpen(false); }}
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

        {/* Input Area */}
        <div className="p-3 sm:p-4 bg-white border-t border-gray-200">
          {!gameState.game_over && !gameState.active_global_event && (
            <div className="mb-2 flex flex-wrap gap-2">
              {isQuickReplyLoading && (!dynamicQuickReplies || dynamicQuickReplies.length === 0) && (
                <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-500 text-xs border border-blue-100">
                  摸鱼助手正在帮你思考回复
                </span>
              )}
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
              {selectedChat === 'group' && fixedQuickReplies.map((text, idx) => {
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
                    ref={text === "老实干活" ? quickCommandRef : undefined}
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
          <div className="relative flex space-x-3">
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
                  : isTyping
                  ? "对方正在思考中..."
                  : `发送给 ${selectedChat === 'group' ? '项目组' : npcList.find(n => n.id === selectedChat)?.name}... (试着说: "帮我修个Bug" 或 "请你喝奶茶")`
              }
              value={input}
              onChange={e => {
                const val = e.target.value;
                setInput(val);
                const pos = e.target.selectionStart ?? val.length;
                const before = val.slice(0, pos);
                const atIdx = before.lastIndexOf("@");
                if (selectedChat === 'group' && atIdx >= 0) {
                  const prev = atIdx > 0 ? before[atIdx - 1] : ' ';
                  const valid = /\s/.test(prev) || atIdx === 0;
                  const tail = before.slice(atIdx + 1);
                  const hasSpace = tail.includes(" ");
                  const query = hasSpace ? "" : tail;
                  if (valid && !hasSpace) {
                    setMentionOpen(true);
                    setMentionStart(atIdx);
                    setMentionQuery(query);
                    setMentionIndex(0);
                  } else {
                    setMentionOpen(false);
                    setMentionQuery("");
                    setMentionStart(null);
                  }
                } else {
                  setMentionOpen(false);
                  setMentionQuery("");
                  setMentionStart(null);
                }
              }}
              onKeyDown={e => {
                if (e.nativeEvent.isComposing) {
                  return;
                }
                if (mentionOpen) {
                  if (e.key === 'ArrowDown' || e.key === 'Tab') {
                    e.preventDefault();
                    setMentionIndex(idx => Math.min(idx + 1, (mentionSuggestions.length || 0) - 1));
                    return;
                  }
                  if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setMentionIndex(idx => Math.max(idx - 1, 0));
                    return;
                  }
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const sel = mentionSuggestions[mentionIndex];
                    if (sel) insertMention(sel.name);
                    return;
                  }
                  if (e.key === 'Escape') {
                    setMentionOpen(false);
                  }
                }
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
            />
            {mentionOpen && selectedChat === 'group' && mentionSuggestions.length > 0 && (
              <div className="absolute bottom-14 left-4 bg-white border border-gray-200 shadow-lg rounded-md z-50 w-56">
                {mentionSuggestions.map((n, idx) => (
                  <div
                    key={n.id}
                    className={`px-3 py-2 text-sm cursor-pointer ${idx === mentionIndex ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}
                    onMouseDown={(ev) => { ev.preventDefault(); insertMention(n.name); }}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-6 h-6 rounded-full ${n.bg} flex items-center justify-center text-white text-xs`}>{n.avatar}</div>
                      <div className="flex-1 truncate">{n.name}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button 
              onClick={sendMessage}
              disabled={inputDisabled || !input.trim()}
              className={`bg-blue-600 text-white px-6 py-3 sm:py-2 rounded-lg hover:bg-blue-700 transition font-medium text-sm flex items-center ${inputDisabled || !input.trim() ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              发送
            </button>
          </div>
        </div>
        </>
        )}
        {isTyping && currentView !== 'chat' && (
          <div className="fixed bottom-4 right-4 z-[200]">
            <div className="px-3 py-2 rounded-lg bg-gray-900 text-white text-xs shadow-lg">
              正在生成回复...
            </div>
          </div>
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
        <div className="sm:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
          <div className="flex items-center justify-around py-2">
            <button className={`p-3 rounded-lg ${currentView === 'chat' ? 'text-blue-600 bg-blue-50' : 'text-gray-600 hover:bg-gray-100'}`} onClick={() => { setCurrentView('chat'); setSelectedChat('group'); }}>
              <MessageSquare className="w-7 h-7"/>
            </button>
            <button className={`p-3 rounded-lg ${currentView === 'workbench' ? 'text-blue-600 bg-blue-50' : 'text-gray-600 hover:bg-gray-100'}`} onClick={() => setCurrentView('workbench')}>
              <LayoutDashboard className="w-7 h-7"/>
            </button>
            <button className={`p-3 rounded-lg ${currentView === 'profile' ? 'text-blue-600 bg-blue-50' : 'text-gray-600 hover:bg-gray-100'}`} onClick={() => setCurrentView('profile')}>
              <MinimalBackpackIcon className="w-7 h-7"/>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
