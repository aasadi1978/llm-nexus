# Migrating Parent Application to Use LLM Nexus

This guide explains how to integrate the newly created `llm-nexus` package into your parent `clean-slate` application.

## Step 1: Install LLM Nexus Locally

From your `clean-slate` project root:

```bash
# Install llm-nexus in editable mode with all providers
pip install -e "./llm-nexus[all]"

# Or install the built wheel
pip install ./llm-nexus/dist/llm_nexus-1.0.0-py3-none-any.whl
```

Verify installation:
```bash
python -c "import llm_nexus; print('✓ LLM Nexus installed successfully')"
```

## Step 2: Create Integration Module

Create `src/integrations/ai_integration.py` if it doesn't already exist:

```python
"""
Integration module for LLM Nexus package.
Connects llm-nexus with clean-slate application infrastructure.
"""
import logging
from llm_nexus.config import AI_CONFIG

_integration_initialized = False


def initialize_llm_integration():
    """
    Initialize LLM Nexus with clean-slate's infrastructure.
    Call this during application startup.
    """
    global _integration_initialized

    if _integration_initialized:
        logging.debug("LLM integration already initialized")
        return

    # Integrate with clean-slate's logger
    try:
        from src.logger.exception_logger import log_exception
        AI_CONFIG.set_exception_logger(log_exception)
        logging.info("✓ LLM Nexus integrated with clean-slate logger")
    except ImportError:
        logging.warning("⚠ Logger integration skipped")

    # Integrate with clean-slate's HTTP clients
    try:
        from src.utils.http_client import HTTP_CLIENT, ASYNC_HTTP_CLIENT
        if HTTP_CLIENT and ASYNC_HTTP_CLIENT:
            AI_CONFIG.set_http_clients(HTTP_CLIENT, ASYNC_HTTP_CLIENT)
            logging.info("✓ LLM Nexus integrated with clean-slate HTTP clients")
    except ImportError:
        logging.info("⚠ HTTP client integration skipped")

    # Integrate with clean-slate's SSL bypass
    try:
        from src.utils.ssl_verification import bypass_ssl_verification
        AI_CONFIG.set_ssl_verification_bypass(bypass_ssl_verification)
        logging.info("✓ LLM Nexus integrated with SSL bypass")
    except ImportError:
        logging.info("⚠ SSL bypass integration skipped")

    _integration_initialized = True
    logging.info("LLM Nexus integration completed")


# Convenience re-exports
from llm_nexus import (
    llm_basic,
    llm_advanced,
    LLM_MODEL_INSTANCE,
    get_token_count,
)

__all__ = [
    'initialize_llm_integration',
    'llm_basic',
    'llm_advanced',
    'LLM_MODEL_INSTANCE',
    'get_token_count',
]
```

## Step 3: Update Application Startup

Modify your application's main entry point to initialize the integration.

**Option A: If using `app/__main__.py` or similar:**

```python
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize LLM integration
from src.integrations.ai_integration import initialize_llm_integration
initialize_llm_integration()

# Rest of your application
from app import main

if __name__ == "__main__":
    main()
```

**Option B: If using Flask's application factory:**

```python
# app/__init__.py
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Initialize LLM integration on first request
    with app.app_context():
        from src.integrations.ai_integration import initialize_llm_integration
        initialize_llm_integration()

    # Register blueprints
    # ...

    return app
```

## Step 4: Update Existing Code

Replace old imports with new ones:

### Before (Old Code):
```python
# OLD - from src.ai
from src.ai import llm_basic, llm_advanced
from src.ai.anthropic_llm import anthropic_basic_model
from src.ai import LLM_MODEL_INSTANCE
```

### After (New Code):
```python
# NEW - from llm_nexus via integration module
from src.integrations.ai_integration import llm_basic, llm_advanced, LLM_MODEL_INSTANCE

# Or import directly from llm_nexus
from llm_nexus import llm_basic, llm_advanced, LLM_MODEL_INSTANCE
```

## Step 5: Update pyproject.toml Dependencies

Add llm-nexus to your clean-slate dependencies:

```toml
# In clean-slate/pyproject.toml
dependencies = [
    # ... existing dependencies ...
    "llm-nexus",  # Add this
]

# Or if installing from local path during development
[tool.setuptools]
packages = find:
# ... existing config ...

# For development
[project.optional-dependencies]
dev = [
    # ... existing dev dependencies ...
]
```

If using editable install, add to your development workflow:
```bash
# In your setup or README
pip install -e "./llm-nexus[all]"
```

## Step 6: Remove Old src/ai Package (Optional)

Once everything is migrated and tested:

1. **Backup first!**
   ```bash
   cp -r src/ai src/ai.backup
   ```

2. **Remove old package** (after confirming new integration works):
   ```bash
   rm -rf src/ai
   ```

3. **Update imports** across your codebase:
   ```bash
   # Find all files importing from src.ai
   grep -r "from src.ai" src/
   grep -r "import src.ai" src/
   ```

4. **Replace with integration imports:**
   - Replace `from src.ai import X` with `from src.integrations.ai_integration import X`
   - Or import directly: `from llm_nexus import X`

## Step 7: Verify Integration

Create a test script to verify everything works:

```python
# test_llm_integration.py
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

def test_integration():
    """Test LLM Nexus integration."""
    from src.integrations.ai_integration import (
        initialize_llm_integration,
        llm_basic,
        llm_advanced,
        LLM_MODEL_INSTANCE
    )

    # Initialize
    initialize_llm_integration()

    # Test models exist
    assert LLM_MODEL_INSTANCE._initialized, "LLM models not initialized"
    print("✓ LLM models initialized")

    if llm_basic:
        print("✓ Basic model available")
    else:
        print("⚠ Basic model not available (check API keys)")

    if llm_advanced:
        print("✓ Advanced model available")
    else:
        print("⚠ Advanced model not available (check API keys)")

    # Test a simple invocation (if API key is set)
    if llm_basic:
        from langchain_core.messages import HumanMessage
        try:
            response = llm_basic.invoke([
                HumanMessage(content="Say 'integration test successful'")
            ])
            print(f"✓ Test response: {response.content[:50]}...")
        except Exception as e:
            print(f"⚠ Test invocation failed: {e}")

    print("\n✅ Integration verification complete!")

if __name__ == "__main__":
    test_integration()
```

Run the test:
```bash
python test_llm_integration.py
```

## Step 8: Update Documentation

Update your clean-slate documentation to reflect the new architecture:

1. Update README.md to mention llm-nexus dependency
2. Update any architecture diagrams
3. Add notes about the llm-nexus package in CLAUDE.md if applicable

## Migration Checklist

- [ ] Install llm-nexus package locally
- [ ] Create integration module (`src/integrations/ai_integration.py`)
- [ ] Update application startup to call `initialize_llm_integration()`
- [ ] Update imports in existing code
- [ ] Test all LLM-related functionality
- [ ] Verify cost tracking still works
- [ ] Verify token counting still works
- [ ] Update pyproject.toml dependencies
- [ ] Run test suite
- [ ] Update documentation
- [ ] (Optional) Remove old src/ai package
- [ ] Commit changes

## Rollback Plan

If you encounter issues:

1. **Restore old src/ai package:**
   ```bash
   cp -r src/ai.backup src/ai
   ```

2. **Uninstall llm-nexus:**
   ```bash
   pip uninstall llm-nexus
   ```

3. **Revert import changes** in your code

4. **Restart application**

## Benefits of Migration

✅ **Portability** - llm-nexus can be used in other projects
✅ **Cleaner Architecture** - Separation of concerns
✅ **Independent Versioning** - llm-nexus can be updated independently
✅ **Easier Testing** - Test LLM functionality in isolation
✅ **Reusability** - Share llm-nexus across multiple applications
✅ **Better Maintenance** - Focused package with clear boundaries

## Support

If you encounter issues during migration:
1. Check this guide thoroughly
2. Review llm-nexus documentation (README.md, INSTALL.md)
3. Check llm-nexus tests for examples
4. Create an issue in the llm-nexus repository

## Example: Complete Migration Diff

**Before:**
```python
# src/some_module.py
from src.ai import llm_basic, llm_advanced, LLM_MODEL_INSTANCE
from src.ai.anthropic_llm import anthropic_token_counter

def process_text(text):
    response = llm_basic.invoke([{"role": "user", "content": text}])
    tokens = anthropic_token_counter(text, "claude-haiku-4-5-20251001")
    return response.content
```

**After:**
```python
# src/some_module.py
from src.integrations.ai_integration import llm_basic, get_token_count

def process_text(text):
    response = llm_basic.invoke([{"role": "user", "content": text}])
    tokens = get_token_count(text, "claude-haiku-4-5-20251001")
    return response.content
```

That's it! Your application now uses the portable llm-nexus package! 🎉
