from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models import GameState, ActionRequest, OnboardRequest
from game import GameManager
import uvicorn
import asyncio
import time
import uuid
from typing import Optional

app = FastAPI(title="MiHoYo Adventure API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class _SessionCtx:
    def __init__(self, manager: GameManager):
        self.manager = manager
        self.lock = asyncio.Lock()
        self.last_access_at = time.monotonic()

_SESSION_COOKIE = "mh_session"
_sessions: dict[str, _SessionCtx] = {}
_sessions_lock = asyncio.Lock()

def _get_session_id_from_request(request: Request) -> Optional[str]:
    header_sid = request.headers.get("x-session-id")
    if header_sid:
        return header_sid.strip() or None
    cookie_sid = request.cookies.get(_SESSION_COOKIE)
    if cookie_sid:
        return cookie_sid.strip() or None
    return None

async def _get_or_create_session(request: Request) -> tuple[str, _SessionCtx, bool]:
    session_id = _get_session_id_from_request(request)
    created = False

    async with _sessions_lock:
        if not session_id:
            session_id = uuid.uuid4().hex
            created = True

        ctx = _sessions.get(session_id)
        if not ctx:
            ctx = _SessionCtx(GameManager())
            _sessions[session_id] = ctx
            created = True

        ctx.last_access_at = time.monotonic()
        return session_id, ctx, created

def _set_session_cookie(response: Response, session_id: str):
    response.set_cookie(
        key=_SESSION_COOKIE,
        value=session_id,
        httponly=True,
        samesite="lax",
        path="/",
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to MiHoYo Adventure API"}

@app.get("/healthz")
def healthz():
    return {"ok": True, "ts": int(time.time())}

@app.post("/api/init", response_model=GameState)
async def init_game(req: OnboardRequest, request: Request, response: Response):
    session_id, ctx, created = await _get_or_create_session(request)
    async with ctx.lock:
        state = await ctx.manager.init_game(req)
    if created:
        _set_session_cookie(response, session_id)
    return state

@app.get("/api/state", response_model=GameState)
async def get_state(request: Request, response: Response):
    session_id, ctx, created = await _get_or_create_session(request)
    async with ctx.lock:
        state = ctx.manager.state
    if created:
        _set_session_cookie(response, session_id)
    return state

@app.post("/api/action", response_model=GameState)
async def action(req: ActionRequest, request: Request, response: Response):
    session_id, ctx, created = await _get_or_create_session(request)
    async with ctx.lock:
        if req.action_type in ("chat", "workbench"):
            state = await ctx.manager.process_text_action(req.content, req.target_npc)
        else:
            state = ctx.manager.state
    if created:
        _set_session_cookie(response, session_id)
    return state

@app.post("/api/event/ack", response_model=GameState)
async def ack_event(request: Request, response: Response):
    session_id, ctx, created = await _get_or_create_session(request)
    async with ctx.lock:
        state = ctx.manager.ack_global_event()
    if created:
        _set_session_cookie(response, session_id)
    return state

@app.post("/api/action/stream")
async def action_stream(req: ActionRequest, request: Request):
    session_id, ctx, created = await _get_or_create_session(request)

    if req.action_type not in ("chat", "workbench"):
        return ctx.manager.state

    async def stream():
        async with ctx.lock:
            async for chunk in ctx.manager.stream_text_action(req.content, req.target_npc):
                yield chunk

    resp = StreamingResponse(stream(), media_type="text/event-stream")
    if created:
        _set_session_cookie(resp, session_id)
    return resp

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
