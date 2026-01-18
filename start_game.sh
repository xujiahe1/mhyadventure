#!/bin/bash
echo ">>> Setting up MiHoYo Adventure..."

# Backend
echo ">>> Installing Backend Dependencies..."
pip install -r backend/requirements.txt

# Frontend
echo ">>> Installing Frontend Dependencies..."
cd frontend
npm install
cd ..

echo ">>> Starting Game Servers..."
# Start Backend
python backend/main.py &
BACKEND_PID=$!

# Start Frontend
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ">>> Game Running!"
echo ">>> Backend: http://localhost:8000"
echo ">>> Frontend: http://localhost:5173"
echo ">>> Press CTRL+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
