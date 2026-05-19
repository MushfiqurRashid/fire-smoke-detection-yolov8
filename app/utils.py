"""
Utility functions for the fire and smoke detection application.

Provides common utilities for image processing, data formatting, etc.
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import logging
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.logger import setup_logger

logger = setup_logger(__name__)


def save_json(data: Dict, output_path: str) -> bool:
    """
    Save data to JSON file.

    Args:
        data: Data to save
        output_path: Path to output file

    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        return False


def load_json(json_path: str) -> Optional[Dict]:
    """
    Load data from JSON file.

    Args:
        json_path: Path to JSON file

    Returns:
        Loaded data or None if failed
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON from {json_path}: {e}")
        return None


def draw_detections(
    image: Image.Image,
    detections: List[Dict],
    confidence_threshold: float = 0.25
) -> Image.Image:
    """
    Draw detection boxes on image.

    Args:
        image: PIL Image
        detections: List of detection dictionaries with 'bbox', 'class', 'confidence'
        confidence_threshold: Minimum confidence to draw

    Returns:
        Image with drawn boxes
    """
    try:
        image_copy = image.copy()
        draw = ImageDraw.Draw(image_copy)
        
        # Color map
        colors = {
            "fire": (255, 0, 0),      # Red
            "smoke": (128, 128, 128)  # Gray
        }

        for detection in detections:
            if detection.get("confidence", 0) < confidence_threshold:
                continue

            bbox = detection.get("bbox", [])
            if not bbox or len(bbox) < 4:
                continue

            class_name = detection.get("class", "unknown")
            confidence = detection.get("confidence", 0)
            
            x1, y1, x2, y2 = bbox[:4]
            color = colors.get(class_name, (0, 255, 0))
            
            # Draw rectangle
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = draw.textbbox((0, 0), label)
            label_width = label_size[2] - label_size[0] + 4
            label_height = label_size[3] - label_size[1] + 4
            
            # Background for text
            draw.rectangle(
                [x1, y1 - label_height, x1 + label_width, y1],
                fill=color
            )
            draw.text((x1 + 2, y1 - label_height + 2), label, fill=(255, 255, 255))

        return image_copy
    except Exception as e:
        logger.warning(f"Failed to draw detections: {e}")
        return image


def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """
    Resize image to max dimensions while maintaining aspect ratio.

    Args:
        image: PIL Image
        max_size: Maximum width/height

    Returns:
        Resized image
    """
    if max(image.size) <= max_size:
        return image

    ratio = max_size / max(image.size)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def pil_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """
    Convert PIL Image to bytes.

    Args:
        image: PIL Image
        format: Image format (PNG, JPEG, etc.)

    Returns:
        Image as bytes
    """
    from io import BytesIO
    
    buffer = BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()


def bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """
    Convert bytes to PIL Image.

    Args:
        image_bytes: Image as bytes

    Returns:
        PIL Image
    """
    from io import BytesIO
    
    return Image.open(BytesIO(image_bytes))


def format_timestamp() -> str:
    """Get formatted current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB."""
    return Path(file_path).stat().st_size / (1024 * 1024)


def validate_image_path(image_path: str) -> bool:
    """Validate image file exists and is readable."""
    try:
        path = Path(image_path)
        if not path.exists():
            return False
        
        # Try to open with PIL
        Image.open(image_path)
        return True
    except Exception as e:
        logger.warning(f"Invalid image path {image_path}: {e}")
        return False


def validate_video_path(video_path: str) -> bool:
    """Validate video file exists and is readable."""
    try:
        path = Path(video_path)
        if not path.exists():
            return False
        
        # Try to open with OpenCV
        cap = cv2.VideoCapture(video_path)
        ret = cap.isOpened()
        cap.release()
        return ret
    except Exception as e:
        logger.warning(f"Invalid video path {video_path}: {e}")
        return False


def calculate_statistics(detections: List[Dict]) -> Dict[str, Any]:
    """
    Calculate statistics from detections.

    Args:
        detections: List of detection dictionaries

    Returns:
        Statistics dictionary
    """
    if not detections:
        return {
            "total_detections": 0,
            "by_class": {}
        }

    class_counts = {}
    confidence_scores = []

    for detection in detections:
        class_name = detection.get("class", "unknown")
        confidence = detection.get("confidence", 0)
        
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
        confidence_scores.append(confidence)

    return {
        "total_detections": len(detections),
        "by_class": class_counts,
        "avg_confidence": np.mean(confidence_scores) if confidence_scores else 0,
        "max_confidence": max(confidence_scores) if confidence_scores else 0,
        "min_confidence": min(confidence_scores) if confidence_scores else 0
    }


def generate_report(
    detections: Dict,
    safety_report: Dict,
    timestamp: Optional[str] = None
) -> str:
    """
    Generate text report from detections and safety analysis.

    Args:
        detections: Detection results
        safety_report: Safety recommendation report
        timestamp: Optional timestamp

    Returns:
        Formatted report string
    """
    if timestamp is None:
        timestamp = format_timestamp()

    report = []
    report.append("=" * 70)
    report.append("FIRE AND SMOKE DETECTION REPORT")
    report.append("=" * 70)
    report.append(f"\nTimestamp: {timestamp}")
    
    # Detection summary
    detection_count = detections.get("detection_count", 0)
    report.append(f"\nDetections Found: {detection_count}")
    
    if detection_count > 0:
        detections_list = detections.get("detections", [])
        stats = calculate_statistics(detections_list)
        
        report.append(f"\nDetection Statistics:")
        report.append(f"  Total: {stats['total_detections']}")
        for class_name, count in stats['by_class'].items():
            report.append(f"  {class_name.capitalize()}: {count}")
        report.append(f"  Average Confidence: {stats['avg_confidence']:.2f}")
    
    # Safety status
    report.append(f"\nSafety Status: {safety_report.get('overall_status', 'UNKNOWN')}")
    
    # Alerts
    alerts = safety_report.get("recommendations", [])
    if alerts:
        report.append(f"\nRecommendations ({len(alerts)}):")
        for i, rec in enumerate(alerts, 1):
            report.append(f"  {i}. {rec}")
    
    report.append("\n" + "=" * 70)
    
    return "\n".join(report)
