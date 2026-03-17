"""
Configuration module for the AI package.
Provides centralized configuration and optional integration hooks.
"""
import logging
from typing import Callable, Optional, Any
from os import getenv


class AIConfig:
    """
    Centralized configuration for the AI package.
    Allows customization through environment variables and dependency injection.
    """

    # Logging configuration
    _exception_logger: Optional[Callable] = None
    _logger = logging.getLogger(__name__)

    # HTTP client configuration
    _http_client: Optional[Any] = None
    _async_http_client: Optional[Any] = None

    # SSL verification
    _ssl_verification_bypass: Optional[Callable] = None

    @classmethod
    def set_exception_logger(cls, logger_func: Callable) -> None:
        """
        Set a custom exception logger function.

        Args:
            logger_func: A callable that takes a message string and logs exceptions.
        """
        cls._exception_logger = logger_func

    @classmethod
    def log_exception(cls, message: str) -> None:
        """
        Log an exception. Uses custom logger if set, otherwise uses standard logging.

        Args:
            message: The error message to log.
        """
        if cls._exception_logger:
            cls._exception_logger(message)
        else:
            cls._logger.exception(message)

    @classmethod
    def set_http_clients(cls, http_client: Any = None, async_http_client: Any = None) -> None:
        """
        Set custom HTTP clients for API calls.

        Args:
            http_client: Synchronous HTTP client.
            async_http_client: Asynchronous HTTP client.
        """
        cls._http_client = http_client
        cls._async_http_client = async_http_client

    @classmethod
    def get_http_client(cls) -> Optional[Any]:
        """Get the configured HTTP client."""
        return cls._http_client

    @classmethod
    def get_async_http_client(cls) -> Optional[Any]:
        """Get the configured async HTTP client."""
        return cls._async_http_client

    @classmethod
    def set_ssl_verification_bypass(cls, bypass_func: Callable) -> None:
        """
        Set a custom SSL verification bypass function.

        Args:
            bypass_func: A callable that configures SSL verification bypass.
        """
        cls._ssl_verification_bypass = bypass_func

    @classmethod
    def bypass_ssl_verification(cls) -> None:
        """
        Bypass SSL verification if a custom function is set.
        Otherwise, does nothing (secure by default).
        """
        if cls._ssl_verification_bypass:
            cls._ssl_verification_bypass()
        else:
            # Secure by default - no SSL bypass
            cls._logger.debug("SSL verification bypass not configured. Using default verification.")


# Environment variable getters with defaults
def get_env(key: str, default: str = "") -> str:
    """Get environment variable with optional default."""
    return getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get environment variable as boolean."""
    value = getenv(key, str(default)).lower()
    return value in ("1", "true", "yes", "on")


def get_env_int(key: str, default: int = 0) -> int:
    """Get environment variable as integer."""
    try:
        return int(getenv(key, str(default)))
    except ValueError:
        return default


# Package configuration
AI_CONFIG = AIConfig()
