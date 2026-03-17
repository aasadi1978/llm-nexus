# 🔗 LLM Nexus

> **Your Central Connection Point for AI Models**

A unified, provider-agnostic Python wrapper for multiple LLM providers including Anthropic (Claude), OpenAI (GPT), Groq, and HuggingFace.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-FedEx%20Express%20Proprietary-purple)](LICENSE)

## ✨ Features

- 🌐 **Multi-Provider Support** - Anthropic, OpenAI, Groq, HuggingFace, Google Vertex AI
- 🔄 **Automatic Fallback** - Tries multiple providers based on available API keys
- 📊 **Cost Tracking** - Built-in usage and cost estimation
- 🔌 **Flexible Integration** - Dependency injection for custom logging and HTTP clients
- ⚡ **LangChain Compatible** - Built on LangChain
- 🚀 **Zero Configuration** - Works out of the box

## 📦 Installation

### Quick Install from Git Repository

```bash
pip install git+https://github.com/alireza-asadi_fedex/llm-nexus.git
```

> **Note**: If you encounter installation issues, please contact the author at alireza.asadi@fedex.com for a pre-built distributable package (e.g., `.whl` file).

### Install with Specific Providers

```bash
pip install "llm-nexus[anthropic]"   # Anthropic only
pip install "llm-nexus[openai]"      # OpenAI only
pip install "llm-nexus[groq]"        # Groq only
pip install "llm-nexus[all]"         # All providers
```

### For Local Development

```bash
pip install -e ".[all,dev]"
```

For more installation options, see [INSTALL.md](INSTALL.md).

## 🚀 Quick Start

```python
from llm_nexus import llm_basic, llm_advanced
from langchain_core.messages import HumanMessage

# Use the basic model
response = llm_basic.invoke([
    HumanMessage(content="What is machine learning?")
])
print(response.content)
```

### Environment Setup

Create `.env` file:

```env
# Anthropic (Primary)
ANTHROPIC_API_KEY=your_key_here

# Or Google Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Or OpenAI (Fallback)
OPENAI_API_KEY=your_key_here
```

## 📚 Advanced Usage

### Embeddings

```python
from llm_nexus.embeddings.embeddings import get_embedding_model

embedding_model = get_embedding_model()
vector = embedding_model.embed_query("What is AI?")
```

### Cost Tracking

```python
from llm_nexus.anthropic_llm.usage_tracker import UsageTracker

tracker = UsageTracker.get_instance()
tracker.initialize(model="claude-haiku-4-5-20251001")

cost = tracker.track_complete_call(
    input_messages=messages,
    output_content=response
)
print(f"Cost: ${cost.total_cost:.6f}")
```

### Token Counting

```python
from llm_nexus import get_token_count

tokens = get_token_count(
    query="Your text here",
    model="claude-haiku-4-5-20251001"
)
```

### Custom Configuration

```python
from llm_nexus.config import AI_CONFIG

# Inject custom logger
AI_CONFIG.set_exception_logger(my_logger)

# Inject HTTP clients
AI_CONFIG.set_http_clients(http_client, async_http_client)
```

## 🏗️ Project Structure

```
llm-nexus/
├── llm_nexus/              # Main package
│   ├── __init__.py        # Auto-configuration
│   ├── config.py          # Configuration system
│   ├── llm.py             # Core LLM singleton
│   ├── anthropic_llm/     # Anthropic support
│   ├── anthropic_vertex/  # Vertex AI support
│   ├── open_ai/           # OpenAI support
│   ├── groq/              # Groq support
│   ├── huggingface/       # HuggingFace support
│   └── embeddings/        # Embedding models
├── tests/                 # Test suite
└── pyproject.toml         # Package config
```

## 🧪 Testing

```bash
pytest
pytest --cov=llm_nexus
```

## 📄 License

FedEx Express Proprietary - see [LICENSE](LICENSE)

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/llm-nexus/issues)
- Email: alireza.asadi@fedex.com
