"""
Configuration management for Fire and Smoke Detection system.

This module handles YAML-based configuration loading and validation.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration handler for the detection system."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration from YAML file.

        Args:
            config_path: Path to config.yaml file. Defaults to configs/config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        logger.info(f"Configuration loaded from {self.config_path}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}. Using defaults.")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config if config else self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}. Using defaults.")
            return self._get_default_config()

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "dataset": {
                "path": "./data",
                "classes": ["smoke", "fire"],
                "train_ratio": 0.7,
                "val_ratio": 0.15,
                "test_ratio": 0.15
            },
            "model": {
                "name": "yolov8n.pt",
                "epochs": 30,
                "batch": 16,
                "imgsz": 640,
                "patience": 20,
                "device": 0
            },
            "thresholds": {
                "fire": 0.60,
                "smoke": 0.50
            },
            "output": {
                "dir": "./outputs",
                "save_plots": True,
                "save_conf_matrix": True
            },
            "logging": {
                "level": "INFO",
                "file": "./outputs/log.txt"
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Key in dot notation (e.g., 'model.epochs')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access to config."""
        return self.config[key]

    def __repr__(self) -> str:
        """String representation of config."""
        return yaml.dump(self.config, default_flow_style=False)


# Global config instance
_config = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get or create global config instance.

    Args:
        config_path: Path to config file (used only on first call)

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reset_config() -> None:
    """Reset global config instance."""
    global _config
    _config = None
