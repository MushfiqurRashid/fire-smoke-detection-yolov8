"""
FastAPI backend for fire and smoke detection.

Provides REST API endpoints for model inference and safety recommendations.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
import logging
from pathlib import Path
import tempfile

from app.predictor import get_predictor
from app.recommender import SafetyRecommender
from app.utils import save_json
from src.config import get_config
from src.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Fire and Smoke Detection API",
    description="Real-time fire and smoke detection using YOLOv8",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global configuration
config = get_config()


# Response models
class Detection(BaseModel):
    """Single detection result."""
    class_name: str = Field(..., alias="class")
    confidence: float
    bbox: List[float]
    model_config = ConfigDict(populate_by_name=True)


class Alert(BaseModel):
    """Alert message."""
    type: str
    message: str
    confidence: float
    severity: str


class PredictionResponse(BaseModel):
    """API response for prediction."""
    status: str
    detections: List[Detection]
    alerts: List[Alert]
    has_critical_alert: bool


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_name: str
    classes: List[str]
    cuda_available: bool


class ClassesResponse(BaseModel):
    """Classes response."""
    classes: List[str]
    total_classes: int


# Initialize predictor on app startup
predictor = None


@app.on_event("startup")
async def startup_event():
    """Initialize predictor on startup."""
    global predictor
    try:
        predictor = get_predictor()
        logger.info("Predictor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize predictor: {e}")


# Health Check Endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check():
    """
    Check API health and model status.

    Returns:
        Health status and model information
    """
    try:
        if predictor is None:
            raise Exception("Predictor not initialized")

        import torch
        model_info = predictor.get_model_info()

        return {
            "status": "healthy",
            "model_name": model_info["model_name"],
            "classes": model_info["classes"],
            "cuda_available": torch.cuda.is_available()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# Classes Endpoint
@app.get(
    "/classes",
    response_model=ClassesResponse,
    tags=["Model Info"],
    summary="Get detection classes"
)
async def get_classes():
    """
    Get available detection classes.

    Returns:
        List of detection classes
    """
    try:
        if predictor is None:
            raise Exception("Predictor not initialized")

        classes = predictor.detector.classes

        return {
            "classes": classes,
            "total_classes": len(classes)
        }
    except Exception as e:
        logger.error(f"Failed to get classes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get classes")


# Image Prediction Endpoint
@app.post(
    "/predict/image",
    response_model=PredictionResponse,
    tags=["Prediction"],
    summary="Predict on image"
)
async def predict_image(
    file: UploadFile = File(...),
    conf: float = Query(0.25, ge=0, le=1, description="Confidence threshold")
):
    """
    Perform detection on uploaded image.

    Args:
        file: Image file (JPEG, PNG, etc.)
        conf: Confidence threshold for detections

    Returns:
        Detection results with alerts and recommendations
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Predictor not initialized")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Run prediction
        result = predictor.predict_image(tmp_path, conf)

        if result.get("status") != "success":
            raise Exception(result.get("error", "Prediction failed"))

        # Clean up
        Path(tmp_path).unlink()

        return {
            "status": "success",
            "detections": [
                {
                    "class_name": d["class"],
                    "confidence": d["confidence"],
                    "bbox": d["bbox"]
                }
                for d in result.get("detections", [])
            ],
            "alerts": result.get("alerts", []),
            "has_critical_alert": result.get("has_critical_alert", False)
        }

    except Exception as e:
        logger.error(f"Image prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Video Prediction Endpoint
@app.post(
    "/predict/video",
    tags=["Prediction"],
    summary="Predict on video"
)
async def predict_video(
    file: UploadFile = File(...),
    conf: float = Query(0.25, ge=0, le=1, description="Confidence threshold")
):
    """
    Perform detection on uploaded video.

    Args:
        file: Video file (MP4, AVI, etc.)
        conf: Confidence threshold for detections

    Returns:
        Video detection results
    """
    if predictor is None:
        raise HTTPException(status_code=503, detail="Predictor not initialized")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Create output path
        output_path = tmp_path.replace(".mp4", "_detected.mp4")

        # Run detection
        result = predictor.detector.detect_video(tmp_path, conf, output_path)

        if result.get("status") != "success":
            raise Exception(result.get("error", "Detection failed"))

        # Clean up
        Path(tmp_path).unlink()

        return {
            "status": "success",
            "message": "Video processed successfully",
            "output_path": output_path
        }

    except Exception as e:
        logger.error(f"Video prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Root Endpoint
@app.get("/", tags=["Info"])
async def root():
    """API root endpoint."""
    return {
        "title": "Fire and Smoke Detection API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "classes": "/classes",
            "predict_image": "/predict/image",
            "predict_video": "/predict/video",
            "docs": "/docs"
        }
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "detail": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
