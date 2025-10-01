#!/bin/bash

# Financial News Dashboard Stop Script

echo "🛑 Stopping Financial News Dashboard servers..."

# Stop backend processes
echo "   Stopping backend (FastAPI)..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null

# Stop frontend processes
echo "   Stopping frontend (HTTP server)..."
pkill -f "python.*http.server" 2>/dev/null

# Wait a moment for processes to stop
sleep 1

# Check if any processes are still running
if pgrep -f "python.*main.py\|python.*http.server\|uvicorn" > /dev/null; then
    echo "⚠️  Some processes may still be running. Force stopping..."
    pkill -9 -f "python.*main.py" 2>/dev/null
    pkill -9 -f "python.*http.server" 2>/dev/null
    pkill -9 -f "uvicorn" 2>/dev/null
fi

echo "✅ All servers stopped successfully!"
