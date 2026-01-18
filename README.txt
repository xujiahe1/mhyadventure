# MiHoYo Adventure (米哈游大冒险)

This is a generated RPG game based on the PRD.

## Tech Stack
- **Frontend**: React + Vite + TailwindCSS
- **Backend**: FastAPI (Python)
- **AI**: DeepSeek (Mocked if API key invalid)

## How to Run
1. Ensure you have `python` (3.8+) and `node` (16+) installed.
2. Run the startup script:
   ```bash
   chmod +x start_game.sh
   ./start_game.sh
   ```
3. Open http://localhost:5173 in your browser.

## Features
- **Onboarding**: Choose your Name, Role (Product/Dev/Ops), and Project (Genshin/Honkai/etc).
- **Workplace OS**: Simulated IM interface.
- **Economy**: Work consumes Energy, gains KPI. Shopping consumes Money.
- **LLM Integration**: Natural language inputs like "修Bug" or "摸鱼" are analyzed for intent.
