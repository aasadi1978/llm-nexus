# Integration Guide for Parent Applications

This guide explains how to integrate the standalone `ai` package into your existing application.

## Overview

The `ai` package is now fully decoupled and can be used as a standalone library. However, if you want to integrate it with your existing application's infrastructure (custom logging, HTTP clients, SSL verification), you can do so through dependency injection.

## Step 1: Install the Package

If using within the same repository:

```python
# Import directly
from src.ai import llm_basic, llm_advanced, LLM_MODEL_INSTANCE
```

If installed as a separate package:

```bash
pip install -e path/to/ai/package
```

Then:

```python
from ai import llm_basic, llm_advanced, LLM_MODEL_INSTANCE
```

## Step 2: Configure Integration Points

### Option A: Use Standalone (No Integration)

The simplest approach - just use the package as-is:

```python
from src.ai import llm_basic, llm_advanced

# Works immediately with environment variables
response = llm_basic.invoke([{"role": "user", "content": "Hello!"}])
```

### Option B: Integrate with Parent Application

If you want to integrate with your application's infrastructure:

```python
from src.ai.config import AI_CONFIG

# 1. Integrate custom exception logging
from src.logger.exception_logger import log_exception
AI_CONFIG.set_exception_logger(log_exception)

# 2. Integrate custom HTTP clients
from src.utils.http_client import HTTP_CLIENT, ASYNC_HTTP_CLIENT
AI_CONFIG.set_http_clients(HTTP_CLIENT, ASYNC_HTTP_CLIENT)

# 3. Integrate SSL verification bypass
from src.utils.ssl_verification import bypass_ssl_verification
AI_CONFIG.set_ssl_verification_bypass(bypass_ssl_verification)

# Now the AI package will use your application's infrastructure
from src.ai import llm_basic, llm_advanced
```

## Step 3: Create Integration Module (Recommended)

Create a dedicated integration module in your application:

**File: `src/integrations/ai_integration.py`**

```python
"""
Integration module for the AI package.
Connects AI package with parent application infrastructure.
"""
import logging
from src.ai.config import AI_CONFIG

def initialize_ai_integration():
    """
    Initialize AI package with parent application's infrastructure.
    Call this during application startup.
    """
    # Setup logging integration
    try:
        from src.logger.exception_logger import log_exception
        AI_CONFIG.set_exception_logger(log_exception)
        logging.info("AI package integrated with application logger")
    except ImportError:
        logging.warning("Application logger not available, using AI package default")

    # Setup HTTP client integration
    try:
        from src.utils.http_client import HTTP_CLIENT, ASYNC_HTTP_CLIENT
        if HTTP_CLIENT and ASYNC_HTTP_CLIENT:
            AI_CONFIG.set_http_clients(HTTP_CLIENT, ASYNC_HTTP_CLIENT)
            logging.info("AI package integrated with application HTTP clients")
    except ImportError:
        logging.info("Application HTTP clients not available, using AI package defaults")

    # Setup SSL verification bypass (if needed)
    try:
        from src.utils.ssl_verification import bypass_ssl_verification
        AI_CONFIG.set_ssl_verification_bypass(bypass_ssl_verification)
        logging.info("AI package integrated with SSL verification bypass")
    except ImportError:
        logging.info("SSL verification bypass not available, using secure defaults")

    logging.info("AI package integration completed")

# Optional: Convenience re-exports
from src.ai import (
    llm_basic,
    llm_advanced,
    LLM_MODEL_INSTANCE,
    get_token_count,
)

__all__ = [
    'initialize_ai_integration',
    'llm_basic',
    'llm_advanced',
    'LLM_MODEL_INSTANCE',
    'get_token_count',
]
```

## Step 4: Initialize During Application Startup

In your application's main entry point:

**File: `app/__main__.py` or `main.py`**

```python
import logging
from src.integrations.ai_integration import initialize_ai_integration

def main():
    # Configure basic logging
    logging.basicConfig(level=logging.INFO)

    # Initialize AI integration
    initialize_ai_integration()

    # Rest of your application startup
    # ...

if __name__ == "__main__":
    main()
```

## Step 5: Use AI Package in Your Application

Now you can use the AI package throughout your application:

```python
# Direct import
from src.ai import llm_basic, llm_advanced

# Or through integration module
from src.integrations.ai_integration import llm_basic, llm_advanced

# Use normally
response = llm_basic.invoke([
    {"role": "user", "content": "Hello!"}
])
```

## Migration from Old Imports

If you're migrating from the old tightly-coupled version:

### Before (Old)
```python
from src.ai.anthropic_llm import anthropic_basic_model
from src.ai.open_ai import openai_basic
from src.logger.exception_logger import log_exception
```

### After (New)
```python
# Option 1: Use new unified interface
from src.ai import llm_basic, llm_advanced

# Option 2: Use integration module
from src.integrations.ai_integration import (
    llm_basic,
    llm_advanced,
    get_token_count
)
```

## Environment Variables

Ensure these environment variables are set:

```env
# Primary provider (Anthropic)
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_BASIC_MODEL=claude-haiku-4-5-20251001
ANTHROPIC_ADVANCED_MODEL=claude-opus-4-1-20250805

# Or Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Fallback providers
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

## Testing the Integration

Create a test to verify integration:

**File: `tests/test_ai_integration.py`**

```python
import pytest
from src.integrations.ai_integration import (
    initialize_ai_integration,
    llm_basic,
    llm_advanced
)

def test_ai_integration():
    """Test AI package integration."""
    # Initialize
    initialize_ai_integration()

    # Verify models are available
    assert llm_basic is not None
    assert llm_advanced is not None

    # Test basic invocation
    from langchain_core.messages import HumanMessage
    response = llm_basic.invoke([
        HumanMessage(content="Say 'test successful'")
    ])

    assert response is not None
    assert response.content
```

## Benefits of This Approach

✅ **Zero Coupling**: AI package has no hard dependencies on parent application
✅ **Flexible Integration**: Choose what to integrate (logging, HTTP, SSL)
✅ **Easy Testing**: Can test AI package independently
✅ **Portable**: Can move AI package to different projects easily
✅ **Optional Integration**: Works standalone or with full integration
✅ **Graceful Degradation**: Falls back to defaults if integration unavailable

## Troubleshooting

### Issue: AI package not finding environment variables

**Solution**: Ensure `.env` file is loaded before importing AI package:

```python
from dotenv import load_dotenv
load_dotenv()  # Load before importing AI

from src.ai import llm_basic
```

### Issue: Custom logger not being used

**Solution**: Call `initialize_ai_integration()` before first AI package use:

```python
from src.integrations.ai_integration import initialize_ai_integration
initialize_ai_integration()  # Must be called first

from src.ai import llm_basic
```

### Issue: SSL certificate errors

**Solution**: Either fix SSL certificates (preferred) or configure bypass:

```python
from src.ai.config import AI_CONFIG
from src.ai.utils import create_ssl_bypass_context

AI_CONFIG.set_ssl_verification_bypass(create_ssl_bypass_context)
```

## Best Practices

1. **Initialize Once**: Call `initialize_ai_integration()` once during startup
2. **Environment First**: Set environment variables before importing AI package
3. **Use Integration Module**: Centralize integration logic in dedicated module
4. **Test Integration**: Write tests to verify integration works correctly
5. **Log Integration Status**: Log which features are integrated successfully
6. **Graceful Fallbacks**: Handle cases where integration dependencies are missing

## Example: Flask Application Integration

```python
# app/__init__.py
from flask import Flask
from src.integrations.ai_integration import initialize_ai_integration

def create_app():
    app = Flask(__name__)

    # Initialize AI integration
    with app.app_context():
        initialize_ai_integration()

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app

# app/routes.py
from flask import Blueprint, request, jsonify
from src.ai import llm_basic

main_bp = Blueprint('main', __name__)

@main_bp.route('/ask', methods=['POST'])
def ask_ai():
    question = request.json.get('question')

    response = llm_basic.invoke([
        {"role": "user", "content": question}
    ])

    return jsonify({
        'answer': response.content
    })
```

## Conclusion

The AI package is now fully portable while still supporting deep integration with parent applications. Choose the integration level that fits your needs:

- **No Integration**: Use standalone with environment variables
- **Partial Integration**: Integrate only what you need (e.g., just logging)
- **Full Integration**: Integrate all infrastructure components

All approaches are supported and work seamlessly.
