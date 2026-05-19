#!/bin/bash

# Fire and Smoke Detection - Streamlit Dashboard Script
# This script runs the Streamlit dashboard

echo "📊 Fire and Smoke Detection - Streamlit Dashboard"
echo "=================================================="

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
PORT=${1:-8501}

# Run Streamlit dashboard
echo "🌐 Starting Streamlit dashboard on port $PORT..."
streamlit run app/streamlit_app.py --server.port $PORT --server.address 0.0.0.0

if [ $? -eq 0 ]; then
    echo "✅ Dashboard stopped successfully!"
else
    echo "❌ Dashboard error!"
    exit 1
fi
