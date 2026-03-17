# AI LLM Wrapper

A unified, provider-agnostic wrapper for multiple LLM providers including Anthropic (Claude), OpenAI (GPT), Groq, and HuggingFace. This package provides a consistent interface for working with different AI models while handling provider-specific configurations and optimizations.

## Features

✨ **Multi-Provider Support**: Works with Anthropic, OpenAI, Groq, HuggingFace, and Google Vertex AI
🔄 **Automatic Fallback**: Tries multiple providers based on available API keys
📊 **Cost Tracking**: Built-in usage and cost estimation for Anthropic models
🔌 **Flexible Integration**: Dependency injection for custom logging and HTTP clients
🎯 **Type-Safe**: Full type hints and Pydantic validation
⚡ **LangChain Compatible**: Built on LangChain for ecosystem compatibility

## Installation

### Basic Installation

```bash
pip install -e .
```

### Provider-Specific Installation

Install only the providers you need:

```bash
# Anthropic (Claude) support
pip install -e ".[anthropic]"

# OpenAI support
pip install -e ".[openai]"

# Groq support
pip install -e ".[groq]"

# HuggingFace support
pip install -e ".[huggingface]"

# Google Vertex AI support
pip install -e ".[vertex]"

# All providers
pip install -e ".[all]"
```

## Quick Start

### Basic Usage

```python
from ai import llm_basic, llm_advanced, LLM_MODEL_INSTANCE
from langchain_core.messages import HumanMessage

# Use the basic model (faster, cheaper)
response = llm_basic.invoke([
    HumanMessage(content="What is machine learning?")
])
print(response.content)

# Use the advanced model (more capable)
response = llm_advanced.invoke([
    HumanMessage(content="Explain quantum computing in detail.")
])
print(response.content)

# Access models through the singleton instance
basic = LLM_MODEL_INSTANCE.basic_model
advanced = LLM_MODEL_INSTANCE.advanced_model
```

### Environment Configuration

The package uses environment variables for configuration. Create a `.env` file:

```env
# Anthropic API (Primary)
ANTHROPIC_API_KEY=your_anthropic_key_here
ANTHROPIC_BASIC_MODEL=claude-haiku-4-5-20251001
ANTHROPIC_ADVANCED_MODEL=claude-opus-4-1-20250805

# Google Vertex AI (Alternative for Anthropic)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
ANTHROPIC_VERTEX_LOCATION=europe-west1

# OpenAI API (Fallback)
OPENAI_API_KEY=your_openai_key_here

# Groq API (Fast, affordable alternative)
GROQ_API_KEY=your_groq_key_here
GROQ_BASIC_MODEL=llama-3.1-8b-instant
GROQ_ADVANCED_MODEL=llama-3.3-70b-versatile

# HuggingFace (Local/offline support)
HUGGINGFACE_API_KEY=your_hf_key_here

# Google Generative AI
GOOGLE_API_KEY=your_google_key_here
```

### Provider Priority

The package tries providers in this order:
1. **Anthropic Vertex AI** (if Google credentials are found)
2. **Anthropic Direct** (if ANTHROPIC_API_KEY is set)
3. **OpenAI** (if OPENAI_API_KEY is set)
4. **Groq** (if GROQ_API_KEY is set)
5. **HuggingFace** (if HUGGINGFACE_API_KEY is set)

## Advanced Usage

### Custom Configuration

```python
from ai.config import AI_CONFIG

# Set custom exception logger
def my_exception_logger(message: str):
    # Your custom logging logic
    print(f"ERROR: {message}")

AI_CONFIG.set_exception_logger(my_exception_logger)

# Set custom HTTP clients (for SSL bypass scenarios)
import httpx

http_client = httpx.Client(verify=False)
async_http_client = httpx.AsyncClient(verify=False)

AI_CONFIG.set_http_clients(http_client, async_http_client)

# Set SSL verification bypass (use cautiously!)
def ssl_bypass():
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

AI_CONFIG.set_ssl_verification_bypass(ssl_bypass)
```

### Embeddings Support

```python
from ai.embeddings.embeddings import get_embedding_model, EmbeddingModel

# Get the configured embedding model
embedding_model = get_embedding_model()

if embedding_model:
    # Embed a single query
    vector = embedding_model.embed_query("What is AI?")

    # Embed multiple documents
    vectors = embedding_model.embed_documents([
        "Document 1 text",
        "Document 2 text",
        "Document 3 text"
    ])
```

Supported embedding providers (tried in order):
- Qwen VL Embeddings (if `USE_QWEN_VL_EMBEDDING=true`)
- Google Vertex AI Embeddings
- Google Generative AI Embeddings
- HuggingFace Embeddings (local, offline-capable)
- OpenAI Embeddings

### Cost Tracking (Anthropic)

```python
from ai.anthropic_llm.usage_tracker import UsageTracker
from langchain_core.messages import HumanMessage

# Create a tracker
tracker = UsageTracker.get_instance()
tracker.initialize(model="claude-haiku-4-5-20251001")

# Track a complete API call
messages = [HumanMessage(content="Explain photosynthesis")]
response_text = "Photosynthesis is the process..."

cost = tracker.track_complete_call(
    input_messages=messages,
    output_content=response_text
)

print(f"Cost: ${cost.total_cost:.6f}")
print(f"Input tokens: {cost.input_tokens}")
print(f"Output tokens: {cost.output_tokens}")

# Get summary
print(tracker.get_summary())
```

### Token Counting

```python
from ai import get_token_count

# Count tokens for a query
token_count = get_token_count(
    query="How does machine learning work?",
    model="claude-haiku-4-5-20251001"
)

print(f"Tokens: {token_count}")
```

## API Reference

### Core Components

#### `LLMModel` (Singleton)

The main singleton class that manages LLM model instances.

```python
from ai import LLM_MODEL_INSTANCE

# Initialize with custom models
LLM_MODEL_INSTANCE.initialize(
    basic_model=my_basic_model,
    advanced_model=my_advanced_model
)

# Access models
basic = LLM_MODEL_INSTANCE.basic_model
advanced = LLM_MODEL_INSTANCE.advanced_model

# Test models
if LLM_MODEL_INSTANCE.test_models():
    print("Models validated successfully")
```

#### `AIConfig`

Configuration and dependency injection.

```python
from ai.config import AI_CONFIG

# Configure logging
AI_CONFIG.set_exception_logger(custom_logger)

# Configure HTTP clients
AI_CONFIG.set_http_clients(http_client, async_http_client)

# Get configured clients
http = AI_CONFIG.get_http_client()
async_http = AI_CONFIG.get_async_http_client()

# Log exceptions
AI_CONFIG.log_exception("Something went wrong")
```

### Provider-Specific Modules

#### Anthropic Direct

```python
from ai.anthropic_llm import (
    anthropic_basic_model,
    anthropic_advanced_model,
    anthropic_token_counter
)

# Token counting
tokens = anthropic_token_counter(
    query="Your query here",
    model="claude-haiku-4-5-20251001"
)
```

#### Anthropic Vertex AI

```python
from ai.anthropic_vertex import (
    anthropic_vertex_basic_model,
    anthropic_vertex_advanced_model
)

# Models are automatically initialized if credentials are found
```

#### OpenAI

```python
from ai.open_ai import (
    openai_basic,
    openai_advanced,
    openai_token_counter
)
```

#### Groq

```python
from ai.groq import (
    groq_basic,
    groq_advanced,
    groq_token_counter
)
```

## Integration with Parent Applications

If you're integrating this package into a larger application, you can provide custom implementations:

```python
from ai.config import AI_CONFIG

# Inject your application's logger
from myapp.logger import exception_logger
AI_CONFIG.set_exception_logger(exception_logger)

# Inject your HTTP clients
from myapp.http import HTTP_CLIENT, ASYNC_HTTP_CLIENT
AI_CONFIG.set_http_clients(HTTP_CLIENT, ASYNC_HTTP_CLIENT)

# Inject SSL bypass if needed
from myapp.utils import bypass_ssl_verification
AI_CONFIG.set_ssl_verification_bypass(bypass_ssl_verification)

# Now use the AI package normally
from ai import llm_basic, llm_advanced
```

## Project Structure

```
ai/
├── __init__.py                 # Main package initialization
├── config.py                   # Configuration and dependency injection
├── llm.py                      # Core LLMModel singleton class
├── utils.py                    # Utility functions (SSL, HTTP clients)
├── pyproject.toml             # Package metadata and dependencies
├── README.md                  # This file
│
├── anthropic_llm/             # Anthropic direct API support
│   ├── __init__.py
│   ├── token_counter.py
│   ├── cost_estimator.py
│   ├── usage_tracker.py
│   └── ...
│
├── anthropic_vertex/          # Anthropic via Google Vertex AI
│   ├── __init__.py
│   ├── initialize_anthropic_vertex_models.py
│   └── token_counter_vertex.py
│
├── open_ai/                   # OpenAI GPT support
│   ├── __init__.py
│   └── openai_embedding.py
│
├── groq/                      # Groq API support
│   ├── __init__.py
│   └── get_models.py
│
├── huggingface/              # HuggingFace models
│   └── __init__.py
│
└── embeddings/               # Embedding models support
    ├── __init__.py
    ├── embeddings.py
    ├── vertex_embedding_wrapper.py
    └── qwenvl_embedding_wrapper.py
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=ai --cov-report=html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [https://github.com/yourusername/ai-llm-wrapper/issues](https://github.com/yourusername/ai-llm-wrapper/issues)
- Documentation: [https://github.com/yourusername/ai-llm-wrapper#readme](https://github.com/yourusername/ai-llm-wrapper#readme)

## Changelog

### Version 1.0.0 (2025-03-16)

- Initial release
- Multi-provider support (Anthropic, OpenAI, Groq, HuggingFace)
- Cost tracking and token counting
- Embedding models support
- Dependency injection for logging and HTTP clients
- Full LangChain compatibility
