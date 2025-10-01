#!/bin/bash

# Financial News Dashboard Startup Script

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

# Check if FINNHUB_API_KEY is set
if [ -z "$FINNHUB_API_KEY" ]; then
    echo "⚠️  Warning: FINNHUB_API_KEY environment variable is not set!"
    echo "   Please set it with: export FINNHUB_API_KEY='your_api_key_here'"
    echo "   Or create a .env file with your API key"
fi

# Start the FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📱 Open frontend/index.html in your browser to use the application"
echo ""

cd backend
python main.py
