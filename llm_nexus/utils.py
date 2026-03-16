"""
Utility functions for the AI package.
Provides SSL bypass and HTTP client creation with no external dependencies.
"""
import logging
import warnings
from typing import Optional, Any

logger = logging.getLogger(__name__)


def create_ssl_bypass_context():
    """
    Create an SSL context that bypasses verification.

    WARNING: This should only be used in development environments.
    Production systems should use proper SSL certificates.
    """
    import ssl
    import urllib3

    # Suppress SSL warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Create unverified context
    ssl._create_default_https_context = ssl._create_unverified_context

    logger.warning("SSL verification has been disabled. This is not recommended for production.")


def create_http_clients(disable_ssl_verification: bool = False) -> tuple[Optional[Any], Optional[Any]]:
    """
    Create HTTP clients for synchronous and asynchronous requests.

    Args:
        disable_ssl_verification: Whether to disable SSL verification (default: False).

    Returns:
        Tuple of (http_client, async_http_client). Returns (None, None) if httpx is not available.
    """
    try:
        import httpx

        if disable_ssl_verification:
            http_client = httpx.Client(verify=False, timeout=60.0)
            async_http_client = httpx.AsyncClient(verify=False, timeout=60.0)
            logger.warning("HTTP clients created with SSL verification disabled.")
        else:
            http_client = httpx.Client(timeout=60.0)
            async_http_client = httpx.AsyncClient(timeout=60.0)
            logger.info("HTTP clients created with SSL verification enabled.")

        return http_client, async_http_client

    except ImportError:
        logger.info("httpx not available. HTTP clients not created.")
        return None, None
