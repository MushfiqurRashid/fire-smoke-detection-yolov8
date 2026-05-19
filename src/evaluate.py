"""
Model evaluation module for fire and smoke detection.

Generates comprehensive evaluation metrics and reports.
"""

import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from ultralytics import YOLO
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import numpy as np
import matplotlib.pyplot as plt
import cv2

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.config import get_config
    from src.logger import setup_logger
else:
    from .config import get_config
    from .logger import setup_logger

logger = setup_logger(__name__)


class FireSmokeEvaluator:
    """Evaluator for fire and smoke detection models."""

    def __init__(self, model_path: str, config_path: Optional[str] = None):
        """
        Initialize evaluator.

        Args:
            model_path: Path to trained model weights
            config_path: Path to configuration file
        """
        self.model = YOLO(model_path)
        self.config = get_config(config_path)
        self.output_dir = Path(self.config.get("output.dir", "./outputs"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.classes = self.config.get("dataset.classes", ["smoke", "fire"])
        logger.info(f"Loaded model from: {model_path}")

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
        temp_dir = Path(tempfile.mkdtemp(prefix="fire_smoke_eval_data_"))
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

    def evaluate(self) -> Dict:
        """
        Evaluate model on test dataset.

        Returns:
            Evaluation results dictionary
        """
        try:
            data_yaml = self._build_ultralytics_data_yaml()

            logger.info(f"Evaluating on dataset: {data_yaml}")

            # Run validation
            results = self.model.val(
                data=str(data_yaml),
                imgsz=self.config.get("model.imgsz", 640),
                batch=self.config.get("model.batch", 16),
                device=0 if self._has_cuda() else "cpu",
                verbose=True
            )

            # Compile results
            eval_results = self._compile_results(results)
            
            # Save evaluation report
            self._save_evaluation_report(eval_results)

            logger.info("Evaluation completed successfully!")
            return eval_results

        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    def _compile_results(self, results) -> Dict:
        """Compile validation results into dictionary."""
        results_dict = {
            "status": "success",
            "metrics": {}
        }

        # Extract metrics from results
        if hasattr(results, 'box'):
            if hasattr(results.box, 'metrics'):
                results_dict["metrics"] = {
                    "mAP50": results.box.metrics.get("mAP50", None),
                    "mAP50-95": results.box.metrics.get("mAP50-95", None),
                }
            
            # Per-class metrics
            if hasattr(results.box, 'ap_class_index'):
                results_dict["per_class_metrics"] = {}
                for i, class_name in enumerate(self.classes):
                    results_dict["per_class_metrics"][class_name] = {
                        "ap50": results.box.ap[i] if i < len(results.box.ap) else None
                    }

        return results_dict

    def _save_evaluation_report(self, results: Dict) -> None:
        """Save evaluation report to file."""
        try:
            report_path = self.output_dir / "evaluation_report.md"
            
            with open(report_path, 'w') as f:
                f.write("# Fire and Smoke Detection Model Evaluation Report\n\n")
                
                if results.get("status") == "success":
                    f.write("## Overall Metrics\n\n")
                    metrics = results.get("metrics", {})
                    for metric_name, value in metrics.items():
                        if value is not None:
                            f.write(f"- **{metric_name}**: {value:.4f}\n")
                    
                    f.write("\n## Per-Class Metrics\n\n")
                    for class_name, class_metrics in results.get("per_class_metrics", {}).items():
                        f.write(f"### {class_name.capitalize()}\n\n")
                        for metric, value in class_metrics.items():
                            if value is not None:
                                f.write(f"- {metric}: {value:.4f}\n")
                else:
                    f.write(f"Evaluation failed: {results.get('error', 'Unknown error')}\n")
            
            logger.info(f"Evaluation report saved to {report_path}")
        except Exception as e:
            logger.warning(f"Could not save evaluation report: {e}")

    @staticmethod
    def _has_cuda() -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False


def main():
    """Main evaluation entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate YOLOv8 fire and smoke detection model"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to model weights (best.pt)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config.yaml file"
    )

    args = parser.parse_args()

    evaluator = FireSmokeEvaluator(model_path=args.model, config_path=args.config)
    results = evaluator.evaluate()
    
    if results.get("status") != "success":
        exit(1)


if __name__ == "__main__":
    main()
