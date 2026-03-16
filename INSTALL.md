# Installation Guide for LLM Nexus

This guide explains how to install and use LLM Nexus in your applications.

## Installation Options

### Option 1: Install from PyPI (When Published)

Once published to PyPI, you can install via pip:

```bash
# Basic installation
pip install llm-nexus

# With specific providers
pip install "llm-nexus[anthropic]"   # Anthropic only
pip install "llm-nexus[openai]"      # OpenAI only
pip install "llm-nexus[groq]"        # Groq only
pip install "llm-nexus[all]"         # All providers
```

### Option 2: Install from Local Directory

For development or before PyPI publication:

```bash
# From the parent directory containing llm-nexus/
pip install -e ./llm-nexus

# With all dependencies
pip install -e "./llm-nexus[all]"
```

### Option 3: Install from Git Repository

```bash
# Install directly from GitHub
pip install git+https://github.com/yourusername/llm-nexus.git

# Or with specific branch/tag
pip install git+https://github.com/yourusername/llm-nexus.git@main
pip install git+https://github.com/yourusername/llm-nexus.git@v1.0.0
```

## Using in Your Applications

### Method 1: Direct Import (Standalone)

The simplest way to use LLM Nexus:

```python
from llm_nexus import llm_basic, llm_advanced, get_token_count
from langchain_core.messages import HumanMessage

# Use immediately
response = llm_basic.invoke([
    HumanMessage(content="Hello!")
])
```

### Method 2: Integration with Application Infrastructure

If you want to integrate with your app's existing logger, HTTP clients, etc.:

**Step 1: Create integration module** (`myapp/integrations/llm_integration.py`)

```python
"""Integration module for LLM Nexus."""
import logging
from llm_nexus.config import AI_CONFIG

def initialize_llm_integration():
    """Initialize LLM Nexus with application infrastructure."""

    # Integrate custom logger (if you have one)
    try:
        from myapp.logger import exception_logger
        AI_CONFIG.set_exception_logger(exception_logger)
        logging.info("✓ LLM Nexus integrated with app logger")
    except ImportError:
        logging.info("Using LLM Nexus default logging")

    # Integrate HTTP clients (if you have custom ones)
    try:
        from myapp.http import HTTP_CLIENT, ASYNC_HTTP_CLIENT
        if HTTP_CLIENT and ASYNC_HTTP_CLIENT:
            AI_CONFIG.set_http_clients(HTTP_CLIENT, ASYNC_HTTP_CLIENT)
            logging.info("✓ LLM Nexus integrated with app HTTP clients")
    except ImportError:
        logging.info("Using LLM Nexus default HTTP handling")

# Re-export for convenience
from llm_nexus import llm_basic, llm_advanced, LLM_MODEL_INSTANCE

__all__ = [
    'initialize_llm_integration',
    'llm_basic',
    'llm_advanced',
    'LLM_MODEL_INSTANCE',
]
```

**Step 2: Initialize during app startup**

```python
# In your main.py or app/__init__.py
from myapp.integrations.llm_integration import initialize_llm_integration

def main():
    # Initialize LLM integration
    initialize_llm_integration()

    # Rest of your app
    # ...

if __name__ == "__main__":
    main()
```

**Step 3: Use throughout your app**

```python
# In any module
from myapp.integrations.llm_integration import llm_basic, llm_advanced

# Use normally - will use your app's infrastructure
response = llm_basic.invoke(messages)
```

## Environment Configuration

### Required Environment Variables

Create a `.env` file or set environment variables:

**Option A: Anthropic Direct API**
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_BASIC_MODEL=claude-haiku-4-5-20251001
ANTHROPIC_ADVANCED_MODEL=claude-opus-4-1-20250805
```

**Option B: Google Vertex AI (for Anthropic)**
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
ANTHROPIC_VERTEX_LOCATION=europe-west1
ANTHROPIC_VERTEX_BASIC_MODEL=claude-haiku-4-5@20251001
ANTHROPIC_VERTEX_ADVANCED_MODEL=claude-opus-4-6@default
```

**Option C: OpenAI**
```env
OPENAI_API_KEY=sk-xxxxx
```

**Option D: Groq**
```env
GROQ_API_KEY=gsk_xxxxx
GROQ_BASIC_MODEL=llama-3.1-8b-instant
GROQ_ADVANCED_MODEL=llama-3.3-70b-versatile
```

**Option E: HuggingFace**
```env
HUGGINGFACE_API_KEY=hf_xxxxx
```

### Loading Environment Variables

```python
# Using python-dotenv
from dotenv import load_dotenv
load_dotenv()  # Load before importing llm_nexus

from llm_nexus import llm_basic
```

## Example: Flask Application

```python
# app/__init__.py
from flask import Flask
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Initialize LLM integration
    from app.integrations import initialize_llm_integration
    with app.app_context():
        initialize_llm_integration()

    # Register routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app

# app/routes.py
from flask import Blueprint, request, jsonify
from llm_nexus import llm_basic

main_bp = Blueprint('main', __name__)

@main_bp.route('/ask', methods=['POST'])
def ask_ai():
    question = request.json.get('question')

    response = llm_basic.invoke([
        {"role": "user", "content": question}
    ])

    return jsonify({'answer': response.content})
```

## Example: FastAPI Application

```python
# main.py
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    from llm_nexus.config import AI_CONFIG
    # Configure if needed
    print("LLM Nexus initialized")

@app.post("/ask")
async def ask_ai(question: str):
    from llm_nexus import llm_basic

    response = llm_basic.invoke([
        {"role": "user", "content": question}
    ])

    return {"answer": response.content}
```

## Example: Django Application

```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# ... your Django settings ...

# myapp/apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Initialize LLM Nexus
        from llm_nexus.config import AI_CONFIG
        # Configure if needed
        print("LLM Nexus initialized")

# myapp/views.py
from django.http import JsonResponse
from llm_nexus import llm_basic

def ask_ai(request):
    question = request.POST.get('question')

    response = llm_basic.invoke([
        {"role": "user", "content": question}
    ])

    return JsonResponse({'answer': response.content})
```

## Building from Source

If you want to build the package yourself:

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-nexus.git
cd llm-nexus

# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# - dist/llm_nexus-1.0.0-py3-none-any.whl
# - dist/llm-nexus-1.0.0.tar.gz

# Install the built wheel
pip install dist/llm_nexus-1.0.0-py3-none-any.whl
```

## Troubleshooting

### Issue: "No module named 'llm_nexus'"

**Solution**: Ensure llm-nexus is installed:
```bash
pip list | grep llm-nexus
pip install llm-nexus  # or pip install -e ./llm-nexus
```

### Issue: "No LLM models have been initialized"

**Solution**: Set at least one provider's API key in environment variables.

### Issue: SSL Certificate Errors

**Solution 1** (Preferred): Fix SSL certificates
**Solution 2** (Dev only): Use SSL bypass
```python
from llm_nexus.utils import create_ssl_bypass_context
from llm_nexus.config import AI_CONFIG

AI_CONFIG.set_ssl_verification_bypass(create_ssl_bypass_context)
```

### Issue: Import errors with LangChain

**Solution**: Ensure LangChain dependencies are installed:
```bash
pip install "llm-nexus[all]"
```

## Verification

Test that installation worked:

```python
# test_installation.py
from llm_nexus import LLM_MODEL_INSTANCE

if LLM_MODEL_INSTANCE._initialized:
    print("✓ LLM Nexus installed and initialized successfully")
    if LLM_MODEL_INSTANCE.basic_model:
        print(f"✓ Basic model available")
    if LLM_MODEL_INSTANCE.advanced_model:
        print(f"✓ Advanced model available")
else:
    print("⚠ LLM Nexus installed but not initialized (check API keys)")
```

Run:
```bash
python test_installation.py
```

## Next Steps

- Read the [README.md](README.md) for full documentation
- Check [CHANGELOG.md](CHANGELOG.md) for version history
- See examples in the `examples/` directory
- Join discussions on GitHub

## Support

If you encounter issues:
1. Check this installation guide
2. Review the [README.md](README.md)
3. Search [GitHub Issues](https://github.com/yourusername/llm-nexus/issues)
4. Create a new issue with details
