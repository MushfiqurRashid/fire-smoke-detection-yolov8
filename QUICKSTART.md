# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Environment Setup (1 minute)

```powershell
# Navigate to project directory
cd g:\fire-smoke-detection-yolov8

# Activate virtual environment (already created)
.\venv\Scripts\Activate.ps1

# Verify Python
python --version
```

### Step 2: Install Dependencies (2 minutes)

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Installation (1 minute)

```powershell
# Test imports
python -c "from ultralytics import YOLO; print('✅ YOLO loaded')"
python -c "import cv2; print('✅ OpenCV loaded')"
python -c "import streamlit; print('✅ Streamlit loaded')"
python -c "import fastapi; print('✅ FastAPI loaded')"
```

### Step 4: Run the Application (1 minute)

**Option A: Streamlit Dashboard (Easiest)**
```powershell
streamlit run app/streamlit_app.py
```
Then open: http://localhost:8501

**Option B: FastAPI Server**
```powershell
uvicorn app.api:app --reload --port 8000
```
Then open: http://localhost:8000/docs

---

## 📂 Project Structure at a Glance

```
fire-smoke-detection-yolov8/
├── 🔧 src/                     # Core modules
│   ├── config.py               # Configuration management
│   ├── logger.py               # Logging setup
│   ├── train.py                # Training pipeline
│   ├── evaluate.py             # Evaluation metrics
│   └── detect.py               # Inference engine
│
├── 💻 app/                     # Applications
│   ├── api.py                  # FastAPI REST API
│   ├── streamlit_app.py        # Streamlit dashboard
│   ├── predictor.py            # Prediction wrapper
│   ├── recommender.py          # Safety recommendations
│   └── utils.py                # Utilities
│
├── ⚙️  configs/                # Configuration files
│   └── config.yaml             # Model and training config
│
├── 🧪 tests/                   # Unit tests
│   ├── test_config.py
│   ├── test_recommender.py
│   └── test_predictor.py
│
├── 📓 notebooks/               # Jupyter notebooks
│   └── exploratory_analysis.ipynb
│
├── 📦 data/                    # Dataset (21,000+ images)
│   ├── train/
│   ├── val/
│   └── test/
│
├── 🐳 Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── 📚 Documentation
    ├── README.md               # Main documentation
    ├── CONTRIBUTING.md         # Contributing guide
    ├── DEPLOYMENT.md           # Deployment guide
    └── QUICKSTART.md           # This file
```

---

## 🎯 Common Commands

### Training
```powershell
# Train YOLOv8 model
python src/train.py

# With custom config
python src/train.py --config configs/config.yaml
```

### Evaluation
```powershell
# Evaluate trained model
python src/evaluate.py --model outputs/fire_smoke_detection/weights/best.pt
```

### Detection
```powershell
# Detect in single image
python src/detect.py --model outputs/fire_smoke_detection/weights/best.pt --source image.jpg

# Detect in video
python src/detect.py --model outputs/fire_smoke_detection/weights/best.pt --source video.mp4

# Batch detection
python src/detect.py --model outputs/fire_smoke_detection/weights/best.pt --source image_folder/
```

### Testing
```powershell
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov=app
```

### Docker
```powershell
# Build image
docker build -t fire-smoke-detection:latest .

# Run with Docker Compose
docker compose up -d

# View logs
docker compose logs -f api
```

---

## 🌐 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Get Classes
```bash
GET http://localhost:8000/classes
```

### Predict Image
```bash
POST http://localhost:8000/predict/image
Content-Type: multipart/form-data
[binary image data]
```

### Predict Video
```bash
POST http://localhost:8000/predict/video
Content-Type: multipart/form-data
[binary video data]
```

---

## 📊 Streamlit Dashboard Features

1. **Home Page** - Overview and system metrics
2. **Detection Page** - Image, video, and webcam detection
3. **About Page** - Project information and technology stack

---

## 🔥 Key Features

✅ Real-time fire and smoke detection
✅ Support for images, videos, and webcams
✅ Automated safety recommendations
✅ Professional REST API
✅ Beautiful Streamlit dashboard
✅ Docker containerization
✅ Comprehensive test suite
✅ Production-ready logging

---

## 📝 Configuration

Edit `configs/config.yaml` to customize:

```yaml
model:
  name: yolov8n.pt          # Model size
  epochs: 30                # Training epochs
  batch: 16                 # Batch size
  imgsz: 640               # Input image size

thresholds:
  fire: 0.60               # Fire confidence threshold
  smoke: 0.50              # Smoke confidence threshold
```

---

## 🐛 Troubleshooting

### Issue: Module not found
```powershell
# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

### Issue: Port already in use
```powershell
# Use different port
streamlit run app/streamlit_app.py --server.port 8502
uvicorn app.api:app --port 8001
```

### Issue: Model not loading
```powershell
# Download model manually
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Issue: CUDA/GPU not found
```powershell
# Use CPU instead
python src/train.py  # Will auto-detect and use CPU
```

---

## 📚 Next Steps

1. **Read the Full README** - [README.md](README.md)
2. **Explore the Notebook** - [notebooks/exploratory_analysis.ipynb](notebooks/exploratory_analysis.ipynb)
3. **Review Contributing Guide** - [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Check Deployment Guide** - [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 💡 Tips

- **First Time?** Start with the Streamlit dashboard for easy testing
- **API Development?** Use FastAPI with `/docs` for interactive testing
- **Training Models?** Check the notebook for detailed steps
- **Deploy to Cloud?** See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🆘 Get Help

- Check logs: `docker compose logs -f`
- Review documentation: See [README.md](README.md)
- Check issues: Review error messages carefully
- Run tests: `pytest tests/ -v` to verify setup

---

## 🎉 You're Ready!

Start the dashboard and begin detecting fire and smoke:

```powershell
streamlit run app/streamlit_app.py
```

Then open http://localhost:8501 in your browser. 🔥
