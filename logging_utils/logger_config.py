"""
Centralized logging configuration utility.
"""
import json
import logging.config
from pathlib import Path
from typing import Optional

# Initialize paths - handling both frozen (PyInstaller) and regular Python execution
SCRIPT_DIR = Path(__file__).resolve().parent


def setup_logger(logger_name: str, config_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger using the centralized configuration.
    
    Args:
        logger_name: Name of the logger to create
        config_file: Optional path to custom config file
        
    Returns:
        Configured logger instance
    """
    if config_file is None:
        config_file = SCRIPT_DIR / "config.json"
    else:
        config_file = Path(config_file)
    
    # Load logging configuration
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Apply the configuration
        logging.config.dictConfig(config)
        
        # Get the logger
        logger = logging.getLogger(logger_name)
        logger.debug(f"Logger '{logger_name}' configured successfully")
        
        return logger
        
    except FileNotFoundError:
        # Fallback to basic configuration
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        logger = logging.getLogger(logger_name)
        logger.warning(f"Config file {config_file} not found, using basic configuration")
        return logger
        
    except json.JSONDecodeError as e:
        # Fallback to basic configuration
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        logger = logging.getLogger(logger_name)
        logger.error(f"Invalid JSON in config file {config_file}: {e}")
        return logger
