from openai import AsyncOpenAI
import os
import random
import json
import time

API_BASE = "https://ark.cn-beijing.volces.com/api/v3"
API_KEY = os.getenv("ARK_API_KEY")
MODEL = os.getenv("ARK_MODEL_ID", "ep-20260118232344-2rdf8")

class LLMService:
    def __init__(self):
        try:
            self.api_key = API_KEY
            if not self.api_key:
                print("Warning: ARK_API_KEY not found in environment variables. Switching to Mock Mode.")
                self.use_mock = True
            else:
                print(f"LLM Client Initializing with Key: {self.api_key[:8]}..., Model: {MODEL}")
                self.client = AsyncOpenAI(base_url=API_BASE, api_key=self.api_key, timeout=20.0)
                self.use_mock = False
        except Exception as e:
            print(f"LLM Client Init Failed: {e}. Switching to Mock Mode.")
            self.use_mock = True

    def _handle_error(self, e):
        """
        Check error type and switch to mock mode if critical (Auth/Billing/Authz).
        Prefer real LLM: network/timeout errors will not permanently enable mock mode.
        """
        err_str = str(e).lower()
        auth_substrings = [
            "401",
            "403",
            "accountoverdue",
            "permissiondenied",
            "unauthorized",
            "authenticationerror",
        ]
        if any(s in err_str for s in auth_substrings):
            print(f"Critical LLM Auth Error detected ({e}). Switching to Mock Mode permanently.")
            self.use_mock = True
        else:
            print(f"LLM Non-critical error: {e}")

    def _map_role_cn(self, role: str) -> str:
        if not role:
            return "员工"
        r = str(role)
        if r == "Dev":
            return "研发工程师"
        if r == "Product":
            return "产品经理"
        if r == "Ops":
            return "综合运营"
        return r

    def _map_project_cn(self, project: str) -> str:
        if not project:
            return "公共项目"
        p = str(project)
        if p == "Genshin":
            return "原神"
        if p == "Honkai3":
            return "崩坏3"
        if p == "HSR":
            return "星穹铁道"
        if p == "ZZZ":
            return "绝区零"
        if p == "HYG":
            return "神秘新作"
        if p == "IAM":
            return "iam"
        if p == "General":
            return "公共项目"
        if p == "HR":
            return "人力资源"
        return p

    async def process_action_stream(self, text: str, player_context: dict, chat_history: list = None, target_npc: dict = None):
        if self.use_mock:
            yield f"<analysis>intent: WORK</analysis>"
            yield f"<narrative>你开始假装工作...</narrative>"
            yield f"<reply npc='System'>摸鱼也是一种工作。</reply>"
            yield f"<effects>mood:1</effects>"
            return

        try:
            player = player_context
            target_name = target_npc.get("name", "System") if target_npc else "None"
            target_traits = target_npc.get("traits", "") if target_npc else ""
            target_project = target_npc.get("project", "") if target_npc else ""
            target_level = target_npc.get("level", "") if target_npc else ""
            target_project = target_npc.get("project", "") if target_npc else ""
            target_level = target_npc.get("level", "") if target_npc else ""
            player_role_cn = self._map_role_cn(player.get("role", "Employee"))
            prompt_context = f"""
            You are the Game Master of a corporate RPG (MiHoYo style).
            IMPORTANT: All output text (narrative, reply) MUST be in Chinese (Simplified).
            
            Task:
            1. Analyze Player Input (Intent & Magnitude).
            2. If a Target NPC is present (or implied), generate their Reply.
            3. Generate System Narrative (Effects).
            
            Context:
            - Player: {player_role_cn}
            - Target NPC: {target_name}（项目组：{target_project}，职级：{target_level}，性格：{target_traits}）
            
            Output Format (Use XML tags for streaming):
            <analysis>
            intent: WORK/REFUSE/SHOP/LEARN/ATTACK/SOCIAL
            magnitude: float (0.0-2.0)
            </analysis>
            <narrative>
            System narrative description here (In Chinese)...
            </narrative>
            <reply npc="NPC_NAME">
            NPC reply content here (In Chinese)...
            </reply>
            <effects>
            mood: int (-10 to 10)
            trust: int (-20 to 20)
            </effects>
            
            Strictly follow this order. Do not output markdown code blocks.
            """
            
            user_payload = {
                "player_input": text,
                "chat_history": chat_history[-5:] if chat_history else []
            }

            t_start = time.perf_counter()
            first_token_time = None
            last_time = None
            stream = await self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                ],
                temperature=0.7,
                max_tokens=500,
                stream=True,
                extra_body={"thinking": {"type": "disabled"}},
            )

            async for chunk in stream:
                choices = getattr(chunk, "choices", None) or []
                for choice in choices:
                    delta = getattr(choice, "delta", None)
                    if not delta:
                        continue
                    content_piece = getattr(delta, "content", None)
                    if content_piece:
                        now = time.perf_counter()
                        if first_token_time is None:
                            first_token_time = now
                        last_time = now
                        yield content_piece

            if first_token_time is not None:
                total = (last_time or time.perf_counter()) - t_start
                first_cost = first_token_time - t_start
                print(f"LLM_STREAM first={first_cost:.3f}s total={total:.3f}s")

        except Exception as e:
            print(f"LLM Stream Error: {e}")
            self._handle_error(e)
            import traceback
            traceback.print_exc()
            yield f"<error>{str(e)}</error>"


    async def process_action(self, text: str, player_context: dict, chat_history: list = None, target_npc: dict = None) -> dict:
        """
        Combined Layer: Analyze intent AND Generate response in one go.
        """
        if self.use_mock:
            # Fallback to mock logic (simulated combined)
            intent_res = self._mock_intent(text)
            response_res = self._mock_response({"target_npc": target_npc, "player_action": text})
            return {**intent_res, **response_res}

        # JSON Schema Definition
        json_schema = """
        {
          "intent": "WORK/REFUSE/SHOP/LEARN/ATTACK/SOCIAL",
          "magnitude": float (0.0-2.0),
          "npc_reply": "String" or null (Roleplay based on traits, REFER to chat_history),
          "npc_name": "String" (Name of NPC replying),
          "system_narrative": "String" (Outcome description),
          "mood_change": int (-10 to 10),
          "trust_change": int (-20 to 20)
        }
        """

        try:
            player = player_context
            target_name = target_npc.get("name", "System") if target_npc else "None"
            target_traits = target_npc.get("traits", "") if target_npc else ""
            target_project = target_npc.get("project", "") if target_npc else ""
            target_level = target_npc.get("level", "") if target_npc else ""
            player_role_cn = self._map_role_cn(player.get("role", "Employee"))
            
            # Construct System Prompt via f-string to avoid .format() issues with JSON braces
            prompt_context = f"""
            You are the Game Master of a corporate RPG (MiHoYo style).
            IMPORTANT: All output text (narrative, reply) MUST be in Chinese (Simplified).
            
            Task:
            1. Analyze Player Input (Intent & Magnitude).
            2. If a Target NPC is present (or implied), generate their Reply.
            3. Generate System Narrative (Effects).
            
            PRD Logic (Intent):
            - "加班/肝/工作": WORK
            - "摸鱼/休息": REFUSE
            - "买/吃/喝": SHOP
            - "学习": LEARN
            - 攻击/辱骂: ATTACK
            - Default: SOCIAL
            
            Context:
            - Player: {player_role_cn}
            - Target NPC: {target_name}（项目组：{target_project}，职级：{target_level}，性格：{target_traits}）
            
            Output JSON:
            {json_schema}
            """
            
            user_payload = {
                "player_input": text,
                "chat_history": chat_history[-5:] if chat_history else []
            }

            t0 = time.perf_counter()
            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                ],
                temperature=0.7,
                max_tokens=300, 
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
            )
            t1 = time.perf_counter()
            print(f"LLM_PROCESS cost={t1 - t0:.3f}s")
            print(f"LLM Response Status: OK")
            # print(f"LLM Raw Content: {response.choices[0].message.content}")
            data = json.loads(response.choices[0].message.content)
            npc_reply = str(data.get("npc_reply") or "").strip()
            if not npc_reply:
                data["npc_reply"] = "收到。"
            npc_name = str(data.get("npc_name") or "").strip()
            if not npc_name:
                npc_name = target_npc.get("name") if target_npc else "System"
                data["npc_name"] = npc_name
            return data
        except Exception as e:
            print(f"LLM Process Error Details: {str(e)}")
            self._handle_error(e)
            import traceback
            traceback.print_exc()
            # Fallback
            intent_res = self._mock_intent(text)
            response_res = self._mock_response({"target_npc": target_npc, "player_action": text})
            return {**intent_res, **response_res}


    async def generate_random_event(self, player_context: dict) -> dict:
        if self.use_mock:
            return {
                "event_msg": "[Mock] 突然发现了一只野生的测试用例。",
                "mood_change": 5,
                "energy_change": 0,
                "money_change": 0
            }

        # JSON Schema
        json_schema = """
        {
            "event_msg": "String (The event description)",
            "mood_change": int (-20 to 20),
            "energy_change": int (-20 to 20),
            "money_change": int (-100 to 100)
        }
        """

        try:
            # Construct System Prompt via f-string
            prompt_context = f"""
            You are the Game Master of a corporate RPG (MiHoYo style).
            IMPORTANT: All output text (event_msg) MUST be in Chinese (Simplified).
            Generate a random workplace event for the player.
            
            Context:
            - Role: {player_context.get("role", "Employee")}
            - Project: {self._map_project_cn(player_context.get("current_project", "General"))}
            - Status: Energy {player_context.get("energy", 0)}, Mood {player_context.get("mood", 0)}, Money {player_context.get("money", 0)}
            
            Task:
            Create a short, interesting random event (1-2 sentences).
            It can be positive (bonus, food, inspiration) or negative (bug, meeting, overtime).
            
            Output JSON:
            {json_schema}
            """

            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": "Generate event"}
                ],
                temperature=0.8,
                max_tokens=200,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM Event Error: {e}")
            self._handle_error(e)
            return {
                "event_msg": "突然感到一阵莫名的波动...",
                "mood_change": 0,
                "energy_change": 0,
                "money_change": 0
            }

    async def generate_group_crosstalk(self, topic_text: str, player_context: dict, npcs: list, chat_history: list = None) -> dict:
        if self.use_mock:
            msgs = []
            for npc in npcs[:2]:
                msgs.append({
                    "content": f"{npc.get('name', '某人')}：关于这个话题，先这样吧（Mock）。"
                })
            return {"messages": msgs}

        json_schema = """
        {
          "messages": [
            {
              "content": "string (Chinese, 5-40 characters, what this NPC says)"
            }
          ]
        }
        """

        try:
            history = chat_history[-8:] if chat_history else []
            prompt_context = f"""
            You are the Game Master of a corporate RPG (MiHoYo style).
            Language: Chinese (Simplified) only.

            The backend系统已经根据玩家输入和NPC标签筛选出了少量“最相关”的NPC,
            现在传给你的是这个精简后的 NPC 列表(npcs 数组)。你不需要再做 NPC 选择,
            但需要为这些 NPC 写台词。

            要点:
            - 使用玩家的最新发言推断话题和情绪(正向/中性/负向)。
            - 根据每个 NPC 的 role / traits / project / relations(对立/上级/下属/合作等)
              决定该 NPC 的语气和立场。
            - messages 数组中的第 i 条内容, 视为 npcs 数组中第 i 个 NPC 的发言。
              必须严格用该 NPC 的身份、人设、立场来写台词。
            - 如果同一个话题中包含对立关系的 NPC, 在负面情绪下可以吵架/互相否定;
              在正向情绪下可以轻微抢功/互相不服; 在中性时保持专业争论。
            - 如果是合作/友好关系, 他们更倾向于互相补充、互相肯定、一起扛事。

            Requirements:
            1. All contents MUST be in Chinese.
            2. Generate 2-4 short messages in total, 优先覆盖 npcs 前 2-3 个角色。
            3. Each message should be 5-40 Chinese characters.
            4. Do not output system narration here, only dialogue content.
            5. 不要在内容里注明说话人姓名或ID, 也不要加冒号前缀。

            Player:
            - Role: {self._map_role_cn(player_context.get("role", "Employee"))}
            - Project: {self._map_project_cn(player_context.get("current_project", "General"))}

            Output JSON:
            {json_schema}
            """

            user_payload = {
                "player_input": topic_text,
                "player": {
                    "role": player_context.get("role"),
                    "current_project": player_context.get("current_project"),
                    "level": player_context.get("level"),
                },
                "npcs": npcs,
                "chat_history": history
            }

            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                ],
                temperature=0.8,
                max_tokens=300,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM Group Crosstalk Error: {e}")
            self._handle_error(e)
            return {"messages": []}

    async def extract_player_topics(self, player_text: str) -> dict:
        if self.use_mock:
            words = [w for w in player_text.replace("，", " ").replace("。", " ").split() if w]
            top = words[:4]
            return {"keywords": top, "raw": player_text}

        json_schema = """
        {
          "keywords": [
            "string (core topic word or short phrase, e.g. IAM邀请制, 访问控制权限, 绩效考核, 研发流程, 产品需求)"
          ]
        }
        """

        try:
            prompt_context = f"""
            You are an assistant for a corporate RPG.
            Language: Chinese (Simplified) only.

            Task:
            - Read the player's latest group chat message.
            - Extract 1-5 compact Chinese keywords/短语 that能最好概括这条消息关注的业务主题,
              比如: "IAM邀请制", "访问控制权限", "IAM研发", "IAM产品", "绩效考核", "项目延期", "加班文化" 等。
            - 这些关键词将被用来在服务端匹配 NPC 的标签(姓名、角色、项目、traits 等),
              所以应尽量贴近玩家话语中出现的实体或概念, 而不是泛泛的情绪词。

            Requirements:
            - 返回 JSON, 仅包含 keywords 字段。
            - 每个 keyword 控制在 2-8 个汉字以内。

            Output JSON:
            {json_schema}
            """

            user_payload = {
                "player_text": player_text
            }

            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                ],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM Topic Extract Error: {e}")
            self._handle_error(e)
            return {"keywords": [], "raw": player_text}

    async def generate_welcome(self, player_name: str, player_role: str, project_name: str, leader_name: str, leader_role: str, leader_traits: str) -> str:
        """
        Dedicated method for generating welcome message to avoid Prompt conflict.
        """
        if self.use_mock:
            return f"@{player_name} 欢迎加入{project_name}。我是{leader_name}。Mock Welcome."

        try:
            player_role_cn = self._map_role_cn(player_role)
            prompt_context = f"""
            You are {leader_name} ({leader_role}), the leader of {project_name} project.
            Traits: {leader_traits}.
            
            Task:
            Welcome a new employee named {player_name}（岗位：{player_role_cn}）to your team.
            
            Requirements:
            1. Language: Chinese (Simplified) ONLY.
            2. Tone: Matches your traits (e.g. strict, friendly, otaku, etc.).
            3. Content: Mention something specific about {project_name} or their role. Assign a simple first task.
            4. Length: Keep it under 60 words.
            5. Format: Start with @{player_name}.
            
            Return ONLY the welcome message content string.
            """

            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": "Generate welcome message."}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Welcome Error: {e}")
            self._handle_error(e)
            import traceback
            traceback.print_exc()
            # Return None to let caller handle fallback
            return None

    async def generate_suggested_replies(self, player_context: dict, chat_history: list = None) -> list:
        if self.use_mock:
            return ["进一步优化日报", "改天再说"]

        json_schema = """
        {
            "suggestions": [
                "string (short reply option, <=10 Chinese characters)",
                "string (short reply option, <=10 Chinese characters)"
            ]
        }
        """

        try:
            history = chat_history[-8:] if chat_history else []
            prompt_context = f"""
            You are the dialogue assistant for a corporate RPG chat.
            Language: Chinese (Simplified) only.

            Task:
            Based on the recent conversation between player and NPCs, propose 2 very short follow-up reply options for the player.

            Requirements:
            1. Strongly condition on the latest NPC feedback and the player's last message.
            2. Each option must be a natural next sentence the player might say.
            3. Focus on concrete actions or decisions, not generic greetings.
            4. Length: each option MUST be within 10 Chinese characters.
            5. Do not include speaker names or punctuation like "：", just the content.

            Player status:
            - Role: {player_context.get("role", "Employee")}
            - Project: {self._map_project_cn(player_context.get("current_project", "General"))}
            - Energy: {player_context.get("energy", 0)}
            - Mood: {player_context.get("mood", 0)}

            Output JSON:
            {json_schema}
            """

            user_payload = {
                "chat_history": history
            }

            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
                ],
                temperature=0.7,
                max_tokens=80,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
            )
            data = json.loads(response.choices[0].message.content)
            suggestions = data.get("suggestions") or []
            cleaned = []
            for s in suggestions:
                if isinstance(s, str):
                    text = s.strip()
                    if text:
                        cleaned.append(text)
                if len(cleaned) >= 2:
                    break
            return cleaned
        except Exception as e:
            print(f"LLM Quick Reply Error: {e}")
            self._handle_error(e)
            return []

    async def score_promotion_answer(self, player_context: dict, review_context: dict) -> dict:
        if self.use_mock:
            base = 70
            level = str(player_context.get("level", "P5"))
            if "P5" in level:
                base = 75
            elif "P6" in level:
                base = 78
            elif "P7" in level:
                base = 80
            elif "P8" in level:
                base = 82
            score = max(50, min(100, base + random.randint(-8, 12)))
            return {
                "score": score,
                "comment": "Mock 打分：整体还可以，逻辑比较清晰。"
            }

        json_schema = """
        {
          "score": int (0-100),
          "comment": "string (short Chinese feedback for the player, <=80 characters)"
        }
        """

        try:
            prompt_context = f"""
            你是一款职场 RPG 游戏中的晋升评委。
            语言：必须使用简体中文回答。

            任务：
            1. 阅读玩家的晋升述职题目和回答。
            2. 综合考虑玩家所在岗位、当前职级、目标职级、项目背景，给出一个 0-100 的分数。
            3. 分数主要看：是否说清了自己做过的事情、是否有结果导向、是否体现和项目/团队目标的关系。

            玩家信息：
            - 岗位：{self._map_role_cn(player_context.get("role", "Employee"))}
            - 当前职级：{player_context.get("level", "P5")}
            - 当前项目：{self._map_project_cn(player_context.get("current_project", "General"))}

            述职背景：
            - 目标晋升职级：{review_context.get("target_level")}
            - 题目：{review_context.get("question")}

            玩家回答：
            \"\"\"{review_context.get("answer")}\"\"\"

            打分规则提示（供你参考，不需要原文输出）：
            - 整体倾向于宽松：只要回答不是敷衍、能看出认真思考，请给出相对偏高分数。
            - P5→P6：只要基本完整、有一些具体细节，建议 70 分及以上。
            - P6→P7：能说明自己对项目有持续贡献，有一定 owner 意识，建议 70-85 分区间。
            - 更高职级：需要体现跨团队影响力、对业务结果负责，好的回答可以在 80 分以上。
            - 只有在回答几乎没有内容、严重跑题或明显敷衍时，才考虑打到 60 分以下。

            输出要求：
            - 只输出一个 JSON 对象，不要有多余文本。
            - score 为 0-100 的整数。
            - comment 为一句简短中文评语（不超过 80 个字），给玩家简单反馈和建议。

            输出 JSON：
            {json_schema}
            """

            payload = {
                "player": {
                    "role": player_context.get("role"),
                    "level": player_context.get("level"),
                    "current_project": player_context.get("current_project"),
                },
                "review": {
                    "target_level": review_context.get("target_level"),
                    "question": review_context.get("question"),
                    "answer": review_context.get("answer"),
                },
            }

            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt_context},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            score = int(data.get("score", 0))
            comment = str(data.get("comment", "")).strip()
            if not comment:
                comment = "本次述职整体表达一般，可以更具体地说明自己的贡献。"
            return {"score": max(0, min(100, score)), "comment": comment}
        except Exception as e:
            print(f"LLM Promotion Review Error: {e}")
            self._handle_error(e)
            return {
                "score": 60,
                "comment": "打分服务异常，默认按及格处理。"
            }


    def _mock_intent(self, text: str) -> dict:
        # Simple keyword matching for mock mode
        # Not used anymore since we have API key hardcoded, but kept for safe fallback
        return {"intent": "SOCIAL", "magnitude": 1.0}

    def _mock_response(self, context: dict) -> dict:
        return {
            "npc_reply": "（离线模式）系统简单帮你应付了一句。",
            "npc_name": "System",
            "system_narrative": "后台生成服务暂不可用，本轮按规则正常结算。",
            "mood_change": 0,
            "trust_change": 0
        }

llm_service = LLMService()
