"""
Logging configuration for the application.
"""
import logging
import sys
from datetime import datetime
from typing import Any, Dict

import structlog

from app.core.config import get_settings

settings = get_settings()


def configure_logging():
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class RequestLogger:
    """Request logging middleware helper."""
    
    @staticmethod
    def log_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Log incoming request details."""
        return {
            "event": "http_request",
            "method": method,
            "url": str(url),
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
    
    @staticmethod
    def log_response(status_code: int, processing_time: float, **kwargs) -> Dict[str, Any]:
        """Log response details."""
        return {
            "event": "http_response", 
            "status_code": status_code,
            "processing_time_ms": round(processing_time * 1000, 2),
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
    
    @staticmethod
    def log_error(error: Exception, **kwargs) -> Dict[str, Any]:
        """Log error details."""
        return {
            "event": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }