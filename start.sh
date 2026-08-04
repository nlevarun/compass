#!/bin/bash

# Compass Startup Script - Simple Version
# Starts backend and frontend in development mode

echo "🚀 Starting Compass..."
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if we're on Mac or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
else
    echo "🐧 Detected Linux"
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Compass..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Step 1: Activate new UI if needed
echo "📱 Step 1: Checking UI..."
if [ -f "frontend/src/App.redesigned.jsx" ] && [ ! -f "frontend/src/App.old.jsx" ]; then
    echo "   Activating new UI..."
    cd frontend/src
    mv App.jsx App.old.jsx 2>/dev/null
    cp App.redesigned.jsx App.jsx
    cd ../..
    echo "   ✅ New UI activated!"
else
    echo "   ✅ UI already configured"
fi

# Step 2: Check backend dependencies
echo ""
echo "🔧 Step 2: Checking backend..."
cd backend

# Check if virtual env exists
if [ ! -d "venv" ]; then
    echo "   ⚠️  Virtual environment not found!"
    echo "   Please run: python3 -m venv venv && source venv/bin/activate && pip install fastapi uvicorn sqlalchemy pydantic python-multipart"
    exit 1
fi

# Initialize database
echo "   Initializing database..."
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="venv/Scripts/python.exe"  # Windows
fi

$PYTHON -c "from database import init_db; init_db(); print('   ✅ Database ready!')" 2>/dev/null || echo "   ✅ Database already initialized"

cd ..

# Step 3: Check frontend dependencies
echo ""
echo "📦 Step 3: Checking frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "   ⚠️  Node modules not found!"
    echo "   Please run: npm install"
    exit 1
fi

echo "   ✅ Frontend dependencies ready"
cd ..

# Step 4: Start servers
echo ""
echo "🚀 Step 4: Starting servers..."
echo "=================================================="
echo ""

# Start backend
echo "Starting backend on http://localhost:8000..."
cd backend
if [ -f "venv/bin/python" ]; then
    source venv/bin/activate
    python main_simple.py &
else
    venv/Scripts/activate
    python main_simple.py &
fi
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "Starting frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a bit for frontend to start
sleep 3

# Show access info
echo ""
echo "=================================================="
echo "✅ Compass is running!"
echo ""
echo "📍 Access points:"
echo "   🌐 Main App:     http://localhost:5173"
echo "   📚 API Docs:     http://localhost:8000/docs"
echo "   🔌 Backend API:  http://localhost:8000/api"
echo ""
echo "💡 The frontend (5173) will connect to backend (8000) automatically"
echo ""
echo "🛑 Press Ctrl+C to stop everything"
echo "=================================================="
echo ""

# Wait for both processes
wait
