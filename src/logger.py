"""
Logging configuration for Fire and Smoke Detection system.

Sets up both console and file logging with consistent formatting.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: str = "INFO"
) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.

    Args:
        name: Logger name (usually __name__)
        log_file: Path to log file. If None, only console logging
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file provided)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class LoggerContext:
    """Context manager for temporary logger level changes."""

    def __init__(self, logger: logging.Logger, level: str = "DEBUG"):
        """
        Initialize logger context.

        Args:
            logger: Logger instance
            level: Temporary logging level
        """
        self.logger = logger
        self.level = getattr(logging, level.upper())
        self.original_level = logger.level

    def __enter__(self):
        """Enter context."""
        self.logger.setLevel(self.level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original level."""
        self.logger.setLevel(self.original_level)
        return False
