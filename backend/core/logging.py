import logging
import sys
from typing import Optional
from config.settings import settings


class LoggerConfig:
    """Configuration for application logging."""
    
    @staticmethod
    def setup_logging(
        level: Optional[int] = None,
        log_format: Optional[str] = None
    ) -> None:
        """
        Setup application logging configuration.
        
        Args:
            level: Logging level (default: INFO if DEBUG is False, DEBUG if DEBUG is True)
            log_format: Custom log format string
        """
        if level is None:
            level = logging.DEBUG if settings.DEBUG else logging.INFO
        
        if log_format is None:
            log_format = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(filename)s:%(lineno)d - %(message)s"
            )
        
        logging.basicConfig(
            level=level,
            format=log_format,
            stream=sys.stdout,
            force=True
        )
        
        # Set specific loggers
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Setup logging on module import
LoggerConfig.setup_logging()
