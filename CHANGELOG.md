# Changelog

All notable changes to llm-nexus will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-16

### Added
- Initial release of llm-nexus
- Multi-provider LLM support (Anthropic, OpenAI, Groq, HuggingFace)
- Unified interface for working with different LLM providers
- Automatic fallback mechanism based on available API keys
- Cost tracking and estimation for Anthropic models
- Token counting utilities
- Embedding models support (Google Vertex AI, Google Generative AI, HuggingFace, OpenAI)
- Dependency injection for custom logging and HTTP clients
- Full LangChain compatibility
- Comprehensive documentation and examples
- Provider-specific configurations via environment variables
- SSL bypass utilities (for development environments)
- Type hints and Pydantic validation throughout
- MIT License

### Features
- **Anthropic Support**: Direct API and Google Vertex AI integration
- **OpenAI Support**: GPT models with full compatibility
- **Groq Support**: Fast, affordable LLM alternative
- **HuggingFace Support**: Local and cloud model execution
- **Embeddings**: Multiple embedding providers with automatic fallback
- **Cost Tracking**: Real-time usage and cost monitoring
- **Flexible Configuration**: Environment-based setup with sensible defaults

### Developer Experience
- Fully typed with mypy support
- Black code formatting
- Ruff linting
- Pytest test suite with coverage
- Comprehensive README with examples
- Integration guides for existing applications

[1.0.0]: https://github.com/yourusername/llm-nexus/releases/tag/v1.0.0
