"""
Training pipeline for YOLOv8 fire and smoke detection models.

Handles model training with configurable hyperparameters and saving of results.
"""

import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional

from ultralytics import YOLO
import torch

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.config import get_config
    from src.logger import setup_logger
else:
    from .config import get_config
    from .logger import setup_logger

logger = setup_logger(__name__)


class FireSmokeTrainer:
    """Trainer for YOLOv8 fire and smoke detection models."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize trainer with configuration.

        Args:
            config_path: Path to configuration file
        """
        self.config = get_config(config_path)
        self.output_dir = Path(self.config.get("output.dir", "./outputs"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check GPU availability
        self.device = 0 if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")

    def _resolve_data_yaml(self) -> Path:
        """Resolve the dataset YAML file from the configured dataset path."""
        dataset_path = Path(self.config.get("dataset.path", "./data"))
        candidates = [
            dataset_path / "data.yaml",
            Path("data.yaml"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            f"Could not find dataset YAML. Checked: {', '.join(str(path) for path in candidates)}"
        )

    def _build_ultralytics_data_yaml(self) -> Path:
        """
        Build a temporary Ultralytics dataset YAML with absolute paths.

        This avoids cross-platform path resolution issues when `data/data.yaml`
        is interpreted relative to different working directories.
        """
        dataset_path = Path(self.config.get("dataset.path", "./data")).resolve()
        temp_dir = Path(tempfile.mkdtemp(prefix="fire_smoke_data_"))
        temp_yaml = temp_dir / "data.yaml"

        classes = self.config.get("dataset.classes", ["smoke", "fire"])
        yaml_content = "\n".join(
            [
                f"path: {dataset_path.as_posix()}",
                "train: train/images",
                "val: val/images",
                "test: test/images",
                "",
                "names:",
                *[f"  - {name}" for name in classes],
                "",
                f"nc: {len(classes)}",
                "",
            ]
        )
        temp_yaml.write_text(yaml_content, encoding="utf-8")
        return temp_yaml

    def train(self, resume: bool = False) -> Dict:
        """
        Train YOLOv8 model for fire and smoke detection.

        Args:
            resume: Whether to resume from last checkpoint

        Returns:
            Training results
        """
        try:
            model_name = self.config.get("model.name", "yolov8n.pt")
            logger.info(f"Loading model: {model_name}")
            model = YOLO(model_name)

            dataset_path = Path(self.config.get("dataset.path", "./data"))
            if not dataset_path.exists():
                raise FileNotFoundError(f"Dataset not found at {dataset_path}")

            data_yaml = self._build_ultralytics_data_yaml()

            logger.info(f"Using dataset: {dataset_path}")

            # Training parameters
            epochs = self.config.get("model.epochs", 30)
            batch_size = self.config.get("model.batch", 16)
            imgsz = self.config.get("model.imgsz", 640)
            patience = self.config.get("model.patience", 20)

            logger.info(f"Training parameters: epochs={epochs}, batch={batch_size}, imgsz={imgsz}")

            # Train model
            results = model.train(
                data=str(data_yaml),
                epochs=epochs,
                imgsz=imgsz,
                batch=batch_size,
                patience=patience,
                device=self.device,
                save=True,
                save_period=10,
                project=str(self.output_dir),
                name="fire_smoke_detection",
                exist_ok=True,
                resume=resume,
                verbose=True
            )

            logger.info("Training completed successfully!")
            logger.info(f"Best weights saved at: {results.save_dir}")

            # Save training summary
            self._save_training_summary(results)

            return {
                "status": "success",
                "model_path": str(results.save_dir),
                "epochs": epochs,
                "best_fitness": float(results.best_fitness) if hasattr(results, 'best_fitness') else None
            }

        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e)
            }

    def _save_training_summary(self, results) -> None:
        """Save training summary to file."""
        try:
            summary_path = self.output_dir / "fire_smoke_detection" / "training_summary.txt"
            with open(summary_path, 'w') as f:
                f.write("=== Fire and Smoke Detection Model Training Summary ===\n\n")
                f.write(f"Model: {self.config.get('model.name')}\n")
                f.write(f"Epochs: {self.config.get('model.epochs')}\n")
                f.write(f"Batch Size: {self.config.get('model.batch')}\n")
                f.write(f"Image Size: {self.config.get('model.imgsz')}\n")
                f.write(f"Device: {self.device}\n")
                
                if hasattr(results, 'best_fitness'):
                    f.write(f"\nBest Fitness: {results.best_fitness:.4f}\n")
                
                f.write("\nTraining completed successfully!\n")
            
            logger.info(f"Training summary saved to {summary_path}")
        except Exception as e:
            logger.warning(f"Could not save training summary: {e}")


def main():
    """Main training entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Train YOLOv8 fire and smoke detection model"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config.yaml file"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint"
    )

    args = parser.parse_args()

    trainer = FireSmokeTrainer(config_path=args.config)
    result = trainer.train(resume=args.resume)
    
    if result["status"] != "success":
        exit(1)


if __name__ == "__main__":
    main()
