"""
Error handling utilities for graceful degradation
"""

import logging
import functools
from typing import Callable, Any, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class MethodologyError(Exception):
    """Base exception for methodology-specific errors"""
    pass

class APIError(MethodologyError):
    """API call related errors"""
    pass

class DataError(MethodologyError):
    """Data processing related errors"""
    pass

class ConfigError(MethodologyError):
    """Configuration related errors"""
    pass

def safe_api_call(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator for safe API calls with retry logic
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                    )
                    
                    # Don't retry for certain errors
                    if isinstance(e, (ConfigError, DataError)):
                        raise
                    
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            
            # All retries failed
            logger.error(f"{func.__name__} failed after {max_retries} attempts")
            raise APIError(f"API call failed after {max_retries} attempts: {str(last_error)}")
        
        return wrapper
    return decorator

def handle_errors(default_return: Any = None, log_errors: bool = True):
    """
    Decorator for graceful error handling
    
    Args:
        default_return: Value to return on error
        log_errors: Whether to log errors
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}", 
                        exc_info=True
                    )
                return default_return
        return wrapper
    return decorator

class ErrorCollector:
    """Collect errors during processing for later analysis"""
    
    def __init__(self):
        self.errors = []
        
    def add_error(self, 
                  error_type: str, 
                  message: str, 
                  context: Optional[Dict[str, Any]] = None) -> None:
        """Add an error to the collection"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "context": context or {}
        }
        self.errors.append(error_entry)
        logger.error(f"{error_type}: {message}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected errors"""
        if not self.errors:
            return {"total_errors": 0, "errors_by_type": {}}
        
        errors_by_type = {}
        for error in self.errors:
            error_type = error["type"]
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
        
        return {
            "total_errors": len(self.errors),
            "errors_by_type": errors_by_type,
            "first_error": self.errors[0],
            "last_error": self.errors[-1],
            "all_errors": self.errors
        }
    
    def has_errors(self) -> bool:
        """Check if any errors were collected"""
        return len(self.errors) > 0
    
    def clear(self) -> None:
        """Clear all collected errors"""
        self.errors = []

def validate_config(config: Dict[str, Any], required_fields: list) -> None:
    """
    Validate configuration dictionary
    
    Args:
        config: Configuration dictionary
        required_fields: List of required field names
        
    Raises:
        ConfigError: If validation fails
    """
    missing_fields = [field for field in required_fields if field not in config]
    
    if missing_fields:
        raise ConfigError(f"Missing required config fields: {', '.join(missing_fields)}")
    
    # Validate specific fields
    if 'models' in config and not isinstance(config['models'], list):
        raise ConfigError("'models' field must be a list")
    
    if 'batch_size' in config and config['batch_size'] <= 0:
        raise ConfigError("'batch_size' must be positive")

import time  # Add this import at the top of the file