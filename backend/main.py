from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models import GameState, ActionRequest, OnboardRequest
from game import game_manager
import uvicorn

app = FastAPI(title="MiHoYo Adventure API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to MiHoYo Adventure API"}

@app.post("/api/init", response_model=GameState)
async def init_game(req: OnboardRequest):
    return await game_manager.init_game(req)

@app.get("/api/state", response_model=GameState)
def get_state():
    return game_manager.state

@app.post("/api/action", response_model=GameState)
async def action(req: ActionRequest):
    if req.action_type in ("chat", "workbench"):
        return await game_manager.process_text_action(req.content, req.target_npc)
    else:
        return game_manager.state

@app.post("/api/event/ack", response_model=GameState)
async def ack_event():
    return game_manager.ack_global_event()

@app.post("/api/action/stream")
async def action_stream(req: ActionRequest):
    if req.action_type in ("chat", "workbench"):
        return StreamingResponse(
            game_manager.stream_text_action(req.content, req.target_npc),
            media_type="text/event-stream"
        )
    else:
        return game_manager.state

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
