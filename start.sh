#!/usr/bin/env bash
set -e

echo "========================================"
echo "  Starting Donut AI"
echo "========================================"
echo ""

# Check .env has API key
if grep -q "GROQ_API_KEY=your_groq_api" .env; then
    echo "ERROR: Please edit .env and add your GROQ_API_KEY"
    echo "Get one at: https://console.groq.com"
    exit 1
fi

# Create data dir
mkdir -p data

# Start backend in background
echo "Starting backend on http://localhost:8000 ..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend
echo "Waiting for backend to start..."
sleep 3

# Start frontend
echo "Starting frontend on http://localhost:3000 ..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  Donut AI is starting!"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Cleanup on exit
cleanup() {
    echo ""
    echo "Stopping Donut AI..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Donut AI stopped."
    exit 0
}

trap cleanup INT TERM

# Wait for either process
wait