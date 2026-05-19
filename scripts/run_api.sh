#!/bin/bash

# Fire and Smoke Detection - FastAPI Server Script
# This script runs the FastAPI backend server

echo "🚀 Fire and Smoke Detection - FastAPI Server"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Could not find a compatible virtual environment activation script."
    exit 1
fi

# Check if model exists
if [ ! -f "outputs/fire_smoke_detection/weights/best.pt" ] && [ ! -f "yolov8n.pt" ]; then
    echo "⚠️  Model not found. You may need to run training first."
    echo "   Running with default model..."
fi

# Get port from argument or use default
PORT=${1:-8000}

# Run FastAPI server
echo "🌐 Starting FastAPI server on port $PORT..."
uvicorn app.api:app --host 0.0.0.0 --port $PORT --reload

if [ $? -eq 0 ]; then
    echo "✅ Server stopped successfully!"
else
    echo "❌ Server error!"
    exit 1
fi
