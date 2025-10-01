#!/bin/bash

# Financial News Dashboard Startup Script

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    pkill -f "python.*main.py" 2>/dev/null
    pkill -f "python.*http.server" 2>/dev/null
    pkill -f "uvicorn" 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Financial News Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Set default API key if not already set
if [ -z "$FINNHUB_API_KEY" ]; then
    echo "🔑 Setting default Finnhub API key..."
    export FINNHUB_API_KEY="d3e9ushr01qrd38tgs0gd3e9ushr01qrd38tgs10"
    echo "   Using provided API key: d3e9ushr01qrd38tgs0gd3e9ushr01qrd38tgs10"
else
    echo "🔑 Using existing FINNHUB_API_KEY environment variable"
fi

# Start the FastAPI server in background
echo "🌐 Starting FastAPI server on http://localhost:8000"
cd backend
python main.py &
BACKEND_PID=$!

# Go back to root directory
cd ..

# Start the frontend server in background
echo "📱 Starting frontend server on http://localhost:3000"
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!

# Go back to root directory
cd ..

echo ""
echo "🎉 Both servers are running!"
echo "   Backend API: http://localhost:8000"
echo "   Frontend UI: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to stop
wait
