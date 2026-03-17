"""
Test script to verify the AI package works standalone.
Run this to ensure the refactoring was successful.
"""
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_imports():
    """Test that all imports work without errors."""
    logger.info("Testing imports...")

    try:
        from . import llm_basic, llm_advanced, LLM_MODEL_INSTANCE, get_token_count
        logger.info("✓ Main package imports successful")
    except Exception as e:
        logger.error(f"✗ Failed to import main package: {e}")
        return False

    try:
        from .config import AI_CONFIG
        logger.info("✓ Config module import successful")
    except Exception as e:
        logger.error(f"✗ Failed to import config: {e}")
        return False

    try:
        from .llm import LLMModel
        logger.info("✓ LLM module import successful")
    except Exception as e:
        logger.error(f"✗ Failed to import LLM module: {e}")
        return False

    try:
        from .utils import create_http_clients, create_ssl_bypass_context
        logger.info("✓ Utils module import successful")
    except Exception as e:
        logger.error(f"✗ Failed to import utils: {e}")
        return False

    return True


def test_configuration():
    """Test configuration system."""
    logger.info("\nTesting configuration system...")

    try:
        from .config import AI_CONFIG

        # Test custom logger
        def test_logger(msg):
            logger.info(f"Custom logger: {msg}")

        AI_CONFIG.set_exception_logger(test_logger)
        AI_CONFIG.log_exception("Test exception log")
        logger.info("✓ Custom logger integration works")

        # Test HTTP client configuration
        AI_CONFIG.set_http_clients(None, None)
        assert AI_CONFIG.get_http_client() is None
        logger.info("✓ HTTP client configuration works")

        return True
    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False


def test_model_initialization():
    """Test that models can be initialized."""
    logger.info("\nTesting model initialization...")

    try:
        from . import LLM_MODEL_INSTANCE

        if LLM_MODEL_INSTANCE._initialized:
            logger.info("✓ LLM models initialized")

            if LLM_MODEL_INSTANCE.basic_model:
                logger.info(f"  - Basic model: Available")
            else:
                logger.warning("  - Basic model: Not available (check API keys)")

            if LLM_MODEL_INSTANCE.advanced_model:
                logger.info(f"  - Advanced model: Available")
            else:
                logger.warning("  - Advanced model: Not available (check API keys)")

            return True
        else:
            logger.warning("⚠ LLM models not initialized (API keys may not be set)")
            return True  # Not an error, just no API keys

    except Exception as e:
        logger.error(f"✗ Model initialization test failed: {e}")
        return False


def test_provider_modules():
    """Test that provider modules can be imported."""
    logger.info("\nTesting provider modules...")

    providers = [
        ('anthropic_llm', 'Anthropic Direct'),
        ('anthropic_vertex', 'Anthropic Vertex AI'),
        ('open_ai', 'OpenAI'),
        ('groq', 'Groq'),
        ('huggingface', 'HuggingFace'),
        ('embeddings', 'Embeddings'),
    ]

    success = True
    for module_name, display_name in providers:
        try:
            __import__(f'.{module_name}', package='ai', fromlist=['*'])
            logger.info(f"✓ {display_name} module imports successfully")
        except Exception as e:
            logger.error(f"✗ {display_name} module import failed: {e}")
            success = False

    return success


def test_no_external_dependencies():
    """Verify that the package has no hard dependencies on parent application."""
    logger.info("\nVerifying no external dependencies...")

    import os
    import re

    ai_dir = Path(__file__).parent
    python_files = list(ai_dir.rglob("*.py"))

    # Pattern to detect problematic imports
    bad_import_pattern = re.compile(r'from\s+src\.(?!ai\.)[\w.]+\s+import')

    issues = []
    for py_file in python_files:
        if '__pycache__' in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = bad_import_pattern.findall(content)
                if matches:
                    issues.append((py_file.relative_to(ai_dir), matches))
        except Exception as e:
            logger.warning(f"Could not read {py_file}: {e}")

    if issues:
        logger.error("✗ Found external dependencies:")
        for file, imports in issues:
            logger.error(f"  {file}: {imports}")
        return False
    else:
        logger.info("✓ No external dependencies found")
        return True


def run_all_tests():
    """Run all tests."""
    logger.info("="*60)
    logger.info("AI Package Standalone Test Suite")
    logger.info("="*60)

    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Model Initialization Test", test_model_initialization),
        ("Provider Modules Test", test_provider_modules),
        ("External Dependencies Test", test_no_external_dependencies),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ {test_name} crashed: {e}", exc_info=True)
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "="*60)
    logger.info("Test Summary")
    logger.info("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! The AI package is standalone and portable.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
