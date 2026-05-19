"""
Tests for configuration module.
"""

import pytest
import tempfile
from pathlib import Path
import yaml

from src.config import Config, get_config, reset_config


def test_config_default():
    """Test loading default configuration."""
    reset_config()
    config = Config(config_path="/nonexistent/path.yaml")
    
    assert config.get("dataset.path") == "./data"
    assert config.get("model.epochs") == 30
    assert config.get("thresholds.fire") == 0.60
    assert config.get("thresholds.smoke") == 0.50


def test_config_from_file():
    """Test loading configuration from YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_data = {
            "model": {"epochs": 50, "batch": 32},
            "thresholds": {"fire": 0.70}
        }
        yaml.dump(config_data, f)
        f.flush()
        temp_path = f.name

    config = Config(config_path=temp_path)
    assert config.get("model.epochs") == 50
    assert config.get("model.batch") == 32
    assert config.get("thresholds.fire") == 0.70

    # Cleanup after the file handle has closed.
    Path(temp_path).unlink()


def test_config_get():
    """Test config.get() method."""
    reset_config()
    config = Config(config_path="/nonexistent/path.yaml")
    
    # Existing key
    assert config.get("dataset.path") == "./data"
    
    # Non-existing key with default
    assert config.get("nonexistent.key", "default") == "default"


def test_config_getitem():
    """Test config[] access."""
    reset_config()
    config = Config(config_path="/nonexistent/path.yaml")
    
    assert config["dataset"]["path"] == "./data"
    assert config["model"]["epochs"] == 30


def test_global_config_singleton():
    """Test global config singleton behavior."""
    reset_config()
    
    config1 = get_config()
    config2 = get_config()
    
    assert config1 is config2


def test_config_repr():
    """Test config string representation."""
    reset_config()
    config = Config(config_path="/nonexistent/path.yaml")
    
    repr_str = repr(config)
    assert "dataset" in repr_str
    assert "model" in repr_str
    assert "thresholds" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
