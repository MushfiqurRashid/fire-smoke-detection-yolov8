#!/bin/bash

# Fire and Smoke Detection - Training Script
# This script trains the YOLOv8 model for fire and smoke detection

echo "🔥 Fire and Smoke Detection - Training Pipeline"
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

# Check if data.yaml exists
if [ ! -f "data/data.yaml" ] && [ ! -f "data.yaml" ]; then
    echo "❌ No dataset YAML found. Expected data/data.yaml or ./data.yaml."
    exit 1
fi

# Run training
echo "📊 Starting YOLOv8 model training..."
python src/train.py --config configs/config.yaml

if [ $? -eq 0 ]; then
    echo "✅ Training completed successfully!"
    echo "📁 Outputs saved to: ./outputs/fire_smoke_detection/"
else
    echo "❌ Training failed!"
    exit 1
fi
