"""
Predictor module for unified inference across different input types.

Wraps the detector for use in FastAPI and Streamlit applications.
"""

import base64
import logging
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image
import numpy as np

from src.config import get_config
from src.detect import FireSmokeDetector
from src.logger import setup_logger

logger = setup_logger(__name__)


class FireSmokePredictor:
    """Unified predictor for fire and smoke detection."""

    def __init__(self, model_path: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize predictor.

        Args:
            model_path: Path to model weights. If None, uses default from config
            config_path: Path to configuration file
        """
        self.config = get_config(config_path)
        
        if model_path is None:
            # Try to find best.pt from training
            output_dir = Path(self.config.get("output.dir", "./outputs"))
            possible_paths = [
                output_dir / "fire_smoke_detection" / "weights" / "best.pt",
                output_dir / "fire_smoke_detection" / "best.pt",
                Path("./yolov8n.pt")
            ]
            
            for path in possible_paths:
                if path.exists():
                    model_path = str(path)
                    break
            
            if model_path is None:
                # Fall back to configured model name, allowing Ultralytics to fetch
                # the checkpoint if the user has not trained custom weights yet.
                model_path = self.config.get("model.name", "yolov8n.pt")
        
        self.detector = FireSmokeDetector(model_path, config_path)
        self.fire_threshold = self.config.get("thresholds.fire", 0.60)
        self.smoke_threshold = self.config.get("thresholds.smoke", 0.50)
        
        logger.info(f"Initialized predictor with model: {model_path}")

    def predict_image(self, image_input: Any, conf: float = 0.25) -> Dict:
        """
        Predict on image input.

        Args:
            image_input: PIL Image, numpy array, file path, or base64 string
            conf: Confidence threshold

        Returns:
            Prediction results with detections and alerts
        """
        try:
            # Convert various input formats to PIL Image
            if isinstance(image_input, str):
                if image_input.startswith('data:image'):
                    # Base64 encoded image
                    image = self._decode_base64_image(image_input)
                else:
                    # File path
                    image = Image.open(image_input)
            elif isinstance(image_input, Image.Image):
                image = image_input
            elif isinstance(image_input, np.ndarray):
                image = Image.fromarray(image_input)
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")

            # Save a temporary image using an OS-safe path.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                temp_path = Path(tmp.name)

            try:
                image.save(temp_path)
                detections = self.detector.detect_image(str(temp_path), conf)
            finally:
                temp_path.unlink(missing_ok=True)
            
            # Add alerts and recommendations
            result = self._add_alerts_and_recommendations(detections)
            result["image_shape"] = image.size
            
            return result

        except Exception as e:
            logger.error(f"Image prediction failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }

    def predict_batch(self, image_dir: str, conf: float = 0.25) -> List[Dict]:
        """
        Predict on batch of images.

        Args:
            image_dir: Directory containing images
            conf: Confidence threshold

        Returns:
            List of prediction results
        """
        results = self.detector.detect_batch(image_dir, conf)
        return [self._add_alerts_and_recommendations(r) for r in results]

    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            "model_name": str(self.detector.model),
            "classes": self.detector.classes,
            "fire_threshold": self.fire_threshold,
            "smoke_threshold": self.smoke_threshold
        }

    def _add_alerts_and_recommendations(self, detections: Dict) -> Dict:
        """Add alert and recommendation information to detections."""
        if detections.get("status") != "success":
            return detections

        alerts = []
        fire_detections = [d for d in detections["detections"] if d["class"] == "fire"]
        smoke_detections = [d for d in detections["detections"] if d["class"] == "smoke"]

        # Check fire threshold
        for fire in fire_detections:
            if fire["confidence"] > self.fire_threshold:
                alerts.append({
                    "type": "fire",
                    "message": "Critical Fire Hazard Detected",
                    "confidence": fire["confidence"],
                    "severity": "CRITICAL"
                })

        # Check smoke threshold
        for smoke in smoke_detections:
            if smoke["confidence"] > self.smoke_threshold:
                alerts.append({
                    "type": "smoke",
                    "message": "Potential Smoke Hazard Detected",
                    "confidence": smoke["confidence"],
                    "severity": "WARNING"
                })

        detections["alerts"] = alerts
        detections["has_critical_alert"] = any(a["severity"] == "CRITICAL" for a in alerts)
        
        return detections

    @staticmethod
    def _decode_base64_image(base64_string: str) -> Image.Image:
        """Decode base64 encoded image."""
        try:
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))
            return image
        except Exception as e:
            raise ValueError(f"Failed to decode base64 image: {e}")


# Global predictor instance
_predictor = None


def get_predictor(model_path: Optional[str] = None, config_path: Optional[str] = None) -> FireSmokePredictor:
    """
    Get or create global predictor instance.

    Args:
        model_path: Path to model weights
        config_path: Path to configuration file

    Returns:
        Predictor instance
    """
    global _predictor
    if _predictor is None:
        _predictor = FireSmokePredictor(model_path, config_path)
    return _predictor


def reset_predictor() -> None:
    """Reset the global predictor instance for tests and reconfiguration."""
    global _predictor
    _predictor = None
