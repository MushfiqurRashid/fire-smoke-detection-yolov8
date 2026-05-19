"""
Tests for predictor module.
"""

import pytest
from pathlib import Path
import tempfile
from PIL import Image
import numpy as np

from app.predictor import FireSmokePredictor, get_predictor


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    return Image.new('RGB', (640, 640), color='red')


@pytest.fixture
def temp_image_file(sample_image):
    """Create a temporary image file."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        sample_image.save(f.name)
        yield f.name
    Path(f.name).unlink()


def test_predictor_initialization():
    """Test predictor initialization."""
    try:
        # This will fail if model is not available, which is expected in test environment
        predictor = FireSmokePredictor(model_path="yolov8n.pt")
        assert predictor is not None
    except FileNotFoundError:
        # Expected if model weights not available
        pytest.skip("Model weights not available")


def test_get_model_info():
    """Test getting model information."""
    try:
        predictor = FireSmokePredictor(model_path="yolov8n.pt")
        info = predictor.get_model_info()
        
        assert "model_name" in info
        assert "classes" in info
        assert "fire_threshold" in info
        assert "smoke_threshold" in info
        assert info["fire_threshold"] == 0.60
        assert info["smoke_threshold"] == 0.50
    except FileNotFoundError:
        pytest.skip("Model weights not available")


def test_decode_base64_image():
    """Test decoding base64 image."""
    import base64
    
    # Create a simple test image
    img = Image.new('RGB', (10, 10), color='red')
    
    # Convert to base64
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    base64_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Test decoding
    decoded = FireSmokePredictor._decode_base64_image(base64_str)
    
    assert isinstance(decoded, Image.Image)
    assert decoded.size == (10, 10)


def test_decode_base64_image_with_prefix():
    """Test decoding base64 image with data URI prefix."""
    import base64
    
    # Create a simple test image
    img = Image.new('RGB', (10, 10), color='blue')
    
    # Convert to base64 with prefix
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    base64_str = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    
    # Test decoding
    decoded = FireSmokePredictor._decode_base64_image(base64_str)
    
    assert isinstance(decoded, Image.Image)
    assert decoded.size == (10, 10)


def test_add_alerts_and_recommendations():
    """Test adding alerts to detections."""
    try:
        predictor = FireSmokePredictor(model_path="yolov8n.pt")
    except FileNotFoundError:
        pytest.skip("Model weights not available")
    
    detections = {
        "status": "success",
        "detections": [
            {"class": "fire", "confidence": 0.92},
            {"class": "smoke", "confidence": 0.48}
        ]
    }
    
    result = predictor._add_alerts_and_recommendations(detections)
    
    assert "alerts" in result
    assert "has_critical_alert" in result
    
    # Fire at 0.92 should trigger alert
    assert len(result["alerts"]) > 0
    
    # Check for fire alert
    fire_alerts = [a for a in result["alerts"] if a["type"] == "fire"]
    assert len(fire_alerts) > 0


def test_add_alerts_failed_detection():
    """Test alerts with failed detection."""
    try:
        predictor = FireSmokePredictor(model_path="yolov8n.pt")
    except FileNotFoundError:
        pytest.skip("Model weights not available")
    
    detections = {
        "status": "failed",
        "error": "Test error"
    }
    
    result = predictor._add_alerts_and_recommendations(detections)
    
    assert result["status"] == "failed"


def test_global_predictor_singleton():
    """Test global predictor singleton."""
    try:
        # Reset to ensure fresh state
        from app.predictor import get_predictor, reset_predictor

        reset_predictor()
        pred1 = get_predictor(model_path="yolov8n.pt")
        pred2 = get_predictor(model_path="yolov8n.pt")
        
        assert pred1 is pred2
    except FileNotFoundError:
        pytest.skip("Model weights not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
