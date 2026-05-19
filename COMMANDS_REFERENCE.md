# 🔥 Fire and Smoke Detection - Commands Reference

## Essential Commands for Daily Use

### 🔧 Environment Setup

```powershell
# Navigate to project
cd g:\fire-smoke-detection-yolov8

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip (if needed)
python -m pip install --upgrade pip

# Install/Update dependencies
pip install -r requirements.txt

# Verify installation
python -c "from ultralytics import YOLO; print('✅ YOLO Ready')"
```

### 🎯 Run Applications

#### Streamlit Dashboard (Recommended for first-time)
```powershell
streamlit run app/streamlit_app.py
# Access: http://localhost:8501
```

#### FastAPI Server
```powershell
# Development (with auto-reload)
uvicorn app.api:app --reload

# Production
uvicorn app.api:app --host 0.0.0.0 --port 8000

# Access: http://localhost:8000/docs
```

#### Both Together (Requires 2 terminals)
```powershell
# Terminal 1 - API
uvicorn app.api:app --reload

# Terminal 2 - Dashboard
streamlit run app/streamlit_app.py
```

### 🐳 Docker Commands

#### Single Service
```powershell
# Build image
docker build -t fire-smoke-detection:latest .

# Run API only
docker run -p 8000:8000 fire-smoke-detection:latest

# Run Dashboard only
docker run -p 8501:8501 fire-smoke-detection:latest \
  streamlit run app/streamlit_app.py
```

#### Full Stack (Recommended)
```powershell
# Start all services
docker compose up -d

# View real-time logs
docker compose logs -f

# View API logs only
docker compose logs -f api

# View Dashboard logs only
docker compose logs -f dashboard

# Stop all services
docker compose down

# Rebuild and restart
docker compose up -d --build

# Remove volumes (clean state)
docker compose down -v
```

### 🏋️ Model Training

#### Basic Training
```powershell
python src/train.py
```

#### Training with Custom Config
```powershell
python src/train.py --config configs/config.yaml
```

#### Resume Interrupted Training
```powershell
python src/train.py --resume
```

#### Training with Verbose Output
```powershell
python src/train.py --verbose
```

### 📊 Model Evaluation

#### Evaluate Trained Model
```powershell
python src/evaluate.py --model outputs/fire_smoke_detection/weights/best.pt
```

#### Evaluate with Custom Config
```powershell
python src/evaluate.py \
  --model outputs/fire_smoke_detection/weights/best.pt \
  --config configs/config.yaml
```

### 🎯 Inference/Detection

#### Single Image
```powershell
python src/detect.py \
  --model outputs/fire_smoke_detection/weights/best.pt \
  --source image.jpg
```

#### Video File
```powershell
python src/detect.py \
  --model outputs/fire_smoke_detection/weights/best.pt \
  --source video.mp4 \
  --output detected_video.mp4
```

#### Batch Images (Folder)
```powershell
python src/detect.py \
  --model outputs/fire_smoke_detection/weights/best.pt \
  --source image_folder/
```

#### With Custom Confidence
```powershell
python src/detect.py \
  --model outputs/fire_smoke_detection/weights/best.pt \
  --source image.jpg \
  --conf 0.50
```

### 🧪 Testing

#### Run All Tests
```powershell
pytest tests/ -v
```

#### Run Specific Test File
```powershell
pytest tests/test_config.py -v
```

#### Run Specific Test Function
```powershell
pytest tests/test_config.py::test_config_default -v
```

#### Run with Coverage Report
```powershell
pytest tests/ --cov=src --cov=app --cov-report=html
```

#### Run with Coverage Display
```powershell
pytest tests/ --cov=src --cov=app --cov-report=term-missing
```

#### Run Tests with Custom Markers
```powershell
pytest tests/ -v -m "not slow"
```

### 📚 API Testing

#### Health Check
```powershell
curl http://localhost:8000/health
```

#### Get Classes
```powershell
curl http://localhost:8000/classes
```

#### Image Prediction (with curl)
```powershell
curl -X POST "http://localhost:8000/predict/image?conf=0.25" `
  -F "file=@image.jpg"
```

#### Video Prediction (with curl)
```powershell
curl -X POST "http://localhost:8000/predict/video?conf=0.25" `
  -F "file=@video.mp4"
```

#### Test with Python
```python
import requests
import json

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Image prediction
with open("image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/predict/image", files=files)
    print(json.dumps(response.json(), indent=2))
```

### 🔍 Debugging & Logging

#### Enable Debug Logging
```powershell
$env:DEBUG = "1"
$env:LOG_LEVEL = "DEBUG"
python src/train.py
```

#### View Configuration
```powershell
python -c "from src.config import get_config; print(get_config())"
```

#### Check Model Loading
```powershell
python -c "from ultralytics import YOLO; m = YOLO('outputs/fire_smoke_detection/weights/best.pt'); print(m)"
```

#### Check PyTorch/CUDA
```powershell
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

#### List Available GPUs
```powershell
python -c "import torch; print(torch.cuda.device_count(), 'GPU(s) available')"
```

### 📁 File Management

#### Check Project Structure
```powershell
tree /L 2  # Windows cmd
# Or use VS Code Explorer
```

#### View Dataset Info
```powershell
python -c "from src.config import get_config; c = get_config(); print(f'Dataset: {c.get(\"dataset.path\")}')"
```

#### List Output Files
```powershell
Get-ChildItem -Path outputs/fire_smoke_detection -Recurse
```

#### Clean Up Outputs (Careful!)
```powershell
Remove-Item -Path outputs/ -Recurse -Force
```

### 📊 Documentation

#### View README
```powershell
# Open in VS Code
code README.md

# Or print to terminal
Get-Content README.md | Less
```

#### View QUICKSTART
```powershell
code QUICKSTART.md
```

#### View API Docs
```
http://localhost:8000/docs  # Swagger UI
http://localhost:8000/redoc # ReDoc
```

### 🚀 Development Workflow

#### Create New Branch
```powershell
git checkout -b feature/my-feature
```

#### Format Code
```powershell
black .
```

#### Check Code Style
```powershell
flake8 . --max-line-length=100
```

#### Sort Imports
```powershell
isort .
```

#### Run Full Development Check
```powershell
black .
isort .
flake8 .
pytest tests/ -v
```

### 🔧 Configuration Management

#### View Current Config
```powershell
code configs/config.yaml
```

#### Edit Configuration
```powershell
# Edit model parameters
# Change epochs, batch size, learning rate, etc.
# Save and restart application
```

#### Reset to Default Config
```powershell
# Replace configs/config.yaml with default values from src/config.py
```

### 📦 Dependency Management

#### Check Installed Packages
```powershell
pip list
```

#### Upgrade All Packages
```powershell
pip install --upgrade -r requirements.txt
```

#### Check for Security Updates
```powershell
pip install safety
safety check
```

#### Create Updated Requirements
```powershell
pip freeze > requirements_new.txt
```

### 🎓 Learning & Exploration

#### Run Jupyter Notebook
```powershell
jupyter notebook notebooks/exploratory_analysis.ipynb
```

#### Run Python REPL with Project Context
```powershell
python -i -c "from src.config import get_config; from app.predictor import FireSmokePredictor; config = get_config()"
```

#### Quick Python Test
```powershell
python -c "
from src.config import get_config
config = get_config()
print('Config loaded:', config.get('dataset.path'))
"
```

### 🐛 Troubleshooting

#### Check Python Version
```powershell
python --version
```

#### Check Virtual Environment
```powershell
Get-Command python  # Should show path in venv
```

#### Clear Python Cache
```powershell
Get-ChildItem -Path . -Include "__pycache__" -Recurse | Remove-Item -Recurse -Force
```

#### Reinstall Dependencies (Clean)
```powershell
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### Check Port Usage
```powershell
netstat -ano | findstr :8000  # Check port 8000
netstat -ano | findstr :8501  # Check port 8501
```

#### Kill Process on Port (if stuck)
```powershell
# Find PID using port 8000
Get-NetTCPConnection -LocalPort 8000 | Stop-Process -Force

# Or get PID and kill
taskkill /PID <PID> /F
```

### 📈 Performance Monitoring

#### Monitor GPU Usage
```powershell
# Windows
nvidia-smi -l 1  # Refresh every 1 second

# Watch mode (if available)
Watch-Output nvidia-smi
```

#### Profile Python Execution
```powershell
python -m cProfile -s cumtime src/train.py
```

#### Memory Usage
```powershell
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

---

## 🎯 Quick Command Sequences

### Setup and Run (First Time)
```powershell
cd g:\fire-smoke-detection-yolov8
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

### Full Development Cycle
```powershell
# 1. Activate
.\venv\Scripts\Activate.ps1

# 2. Format code
black .

# 3. Run tests
pytest tests/ -v

# 4. Train model
python src/train.py

# 5. Evaluate
python src/evaluate.py --model outputs/fire_smoke_detection/weights/best.pt

# 6. Run app
streamlit run app/streamlit_app.py
```

### Docker Production Deployment
```powershell
# 1. Build
docker build -t fire-smoke-detection:latest .

# 2. Test locally
docker run -p 8000:8000 -p 8501:8501 fire-smoke-detection:latest

# 3. Deploy stack
docker compose up -d --build

# 4. Monitor
docker compose logs -f

# 5. Stop
docker compose down
```

---

## 🆘 Help Commands

```powershell
# Get Python help
python --help
pip --help

# Get module help
python -c "import ultralytics; help(ultralytics.YOLO)"

# View docstrings
python -c "from src.train import FireSmokeTrainer; help(FireSmokeTrainer)"

# Check documentation
code README.md
code QUICKSTART.md
code DEPLOYMENT.md
```

---

**Save this file for quick reference!** ⭐
