"""Test basic imports work."""
import pytest


def test_main_imports():
    """Test that main package imports work."""
    from llm_nexus import LLM_MODEL_INSTANCE, get_token_count

    assert LLM_MODEL_INSTANCE is not None
    assert get_token_count is not None


def test_config_import():
    """Test that config module imports work."""
    from llm_nexus.config import AI_CONFIG

    assert AI_CONFIG is not None


def test_llm_model_import():
    """Test that LLM model imports work."""
    from llm_nexus.llm import LLMModel

    assert LLMModel is not None


def test_utils_import():
    """Test that utils imports work."""
    from llm_nexus.utils import create_http_clients, create_ssl_bypass_context

    assert create_http_clients is not None
    assert create_ssl_bypass_context is not None


def test_provider_modules_exist():
    """Test that all provider modules can be imported."""
    providers = [
        'anthropic_llm',
        'anthropic_vertex',
        'open_ai',
        'groq',
        'huggingface',
        'embeddings',
    ]

    for provider in providers:
        try:
            __import__(f'llm_nexus.{provider}')
        except ImportError as e:
            pytest.fail(f"Failed to import llm_nexus.{provider}: {e}")


def test_config_methods():
    """Test configuration methods."""
    from llm_nexus.config import AI_CONFIG

    # Test logger injection
    def test_logger(msg):
        pass

    AI_CONFIG.set_exception_logger(test_logger)
    AI_CONFIG.log_exception("test")  # Should not raise

    # Test HTTP client injection
    AI_CONFIG.set_http_clients(None, None)
    assert AI_CONFIG.get_http_client() is None
    assert AI_CONFIG.get_async_http_client() is None
