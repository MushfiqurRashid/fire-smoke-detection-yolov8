"""
Detection and inference module for fire and smoke detection.

Handles inference on images, videos, and webcam streams.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.config import get_config
    from src.logger import setup_logger
else:
    from .config import get_config
    from .logger import setup_logger

logger = setup_logger(__name__)


class FireSmokeDetector:
    """Detector for fire and smoke in images and videos."""

    def __init__(self, model_path: str, config_path: Optional[str] = None):
        """
        Initialize detector.

        Args:
            model_path: Path to trained model weights
            config_path: Path to configuration file
        """
        self.model = YOLO(model_path)
        self.config = get_config(config_path)
        
        self.fire_threshold = self.config.get("thresholds.fire", 0.60)
        self.smoke_threshold = self.config.get("thresholds.smoke", 0.50)
        self.classes = self.config.get("dataset.classes", ["smoke", "fire"])
        self.class_to_idx = {name: idx for idx, name in enumerate(self.classes)}
        
        logger.info(f"Loaded detector from: {model_path}")
        logger.info(f"Thresholds - Fire: {self.fire_threshold}, Smoke: {self.smoke_threshold}")

    def detect_image(self, image_path: str, conf: float = 0.25) -> Dict:
        """
        Detect fire and smoke in a single image.

        Args:
            image_path: Path to image file
            conf: Confidence threshold for detection

        Returns:
            Detection results dictionary
        """
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            logger.info(f"Processing image: {image_path}")
            
            # Run inference
            results = self.model.predict(
                source=str(image_path),
                conf=conf,
                verbose=False
            )

            detections = self._parse_results(results[0], image_path)
            logger.info(f"Found {len(detections['detections'])} detections")
            
            return detections

        except Exception as e:
            logger.error(f"Detection failed for {image_path}: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }

    def detect_batch(self, image_dir: str, conf: float = 0.25) -> List[Dict]:
        """
        Detect fire and smoke in multiple images.

        Args:
            image_dir: Directory containing images
            conf: Confidence threshold

        Returns:
            List of detection results
        """
        image_dir = Path(image_dir)
        if not image_dir.exists():
            raise FileNotFoundError(f"Directory not found: {image_dir}")

        results = []
        image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
        
        logger.info(f"Processing {len(image_files)} images from {image_dir}")
        
        for image_path in image_files:
            result = self.detect_image(str(image_path), conf)
            results.append(result)

        logger.info(f"Batch processing completed. Processed {len(results)} images")
        return results

    def detect_video(
        self,
        video_path: str,
        conf: float = 0.25,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Detect fire and smoke in a video file.

        Args:
            video_path: Path to video file
            conf: Confidence threshold
            output_path: Path to save annotated video (optional)

        Returns:
            Detection results
        """
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Video not found: {video_path}")

            logger.info(f"Processing video: {video_path}")
            
            cap = cv2.VideoCapture(str(video_path))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Setup video writer if output requested
            writer = None
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

            all_detections = []
            frame_count = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                
                # Run inference on frame
                results = self.model.predict(
                    source=frame,
                    conf=conf,
                    verbose=False
                )

                detections = self._parse_frame_results(results[0], frame_count)
                all_detections.append(detections)

                # Annotate frame
                annotated_frame = results[0].plot()
                
                # Write to output video
                if writer:
                    writer.write(annotated_frame)

                if frame_count % 30 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames")

            cap.release()
            if writer:
                writer.release()
                logger.info(f"Annotated video saved to {output_path}")

            return {
                "status": "success",
                "video_path": str(video_path),
                "total_frames": total_frames,
                "detections_by_frame": all_detections
            }

        except Exception as e:
            logger.error(f"Video processing failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }

    def detect_webcam(self, duration: int = 30, conf: float = 0.25) -> Dict:
        """
        Detect fire and smoke from webcam stream.

        Args:
            duration: Duration in seconds to capture
            conf: Confidence threshold

        Returns:
            Detection results
        """
        try:
            logger.info(f"Starting webcam capture for {duration} seconds")
            
            cap = cv2.VideoCapture(0)
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
            
            all_detections = []
            frame_count = 0
            start_time = None

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if start_time is None:
                    start_time = cv2.getTickCount()

                frame_count += 1
                
                # Run inference
                results = self.model.predict(
                    source=frame,
                    conf=conf,
                    verbose=False
                )

                detections = self._parse_frame_results(results[0], frame_count)
                all_detections.append(detections)

                # Display annotated frame
                annotated = results[0].plot()
                cv2.imshow("Fire and Smoke Detection - Webcam", annotated)

                # Check time
                elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                if elapsed > duration:
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

            return {
                "status": "success",
                "total_frames": frame_count,
                "detections_by_frame": all_detections
            }

        except Exception as e:
            logger.error(f"Webcam capture failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }

    def _parse_results(self, result, image_path: Path) -> Dict:
        """Parse detection results from a single image."""
        detections = []
        
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = self.classes[class_id] if class_id < len(self.classes) else "unknown"
                confidence = float(box.conf[0])
                
                detections.append({
                    "class": class_name,
                    "confidence": confidence,
                    "bbox": box.xyxy[0].tolist()
                })

        return {
            "status": "success",
            "image_path": str(image_path),
            "detections": detections
        }

    def _parse_frame_results(self, result, frame_count: int) -> Dict:
        """Parse detection results from a single video frame."""
        detections = []
        
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = self.classes[class_id] if class_id < len(self.classes) else "unknown"
                confidence = float(box.conf[0])
                
                detections.append({
                    "class": class_name,
                    "confidence": confidence
                })

        return {
            "frame": frame_count,
            "detections": detections
        }


def main():
    """Main detection entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect fire and smoke in images/videos"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to model weights"
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to image, video, or directory"
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save annotated output"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config.yaml file"
    )

    args = parser.parse_args()

    detector = FireSmokeDetector(model_path=args.model, config_path=args.config)
    
    source_path = Path(args.source)
    
    if source_path.is_file() and source_path.suffix.lower() in ['.mp4', '.avi', '.mov']:
        result = detector.detect_video(args.source, args.conf, args.output)
    elif source_path.is_file():
        result = detector.detect_image(args.source, args.conf)
    elif source_path.is_dir():
        result = detector.detect_batch(args.source, args.conf)
    else:
        logger.error(f"Invalid source: {args.source}")
        exit(1)

    if result.get("status") != "success":
        exit(1)


if __name__ == "__main__":
    main()
