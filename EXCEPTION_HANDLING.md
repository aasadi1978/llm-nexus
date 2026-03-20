# Exception Handling in llm-nexus

This document describes the custom exceptions provided by llm-nexus and how to handle them.

## Custom Exceptions

### `MissingAPIKeyError`

Raised when no API key is found for a specific LLM provider.

**Attributes:**
- `provider`: The name of the provider (e.g., "Anthropic", "OpenAI", "Groq")
- `env_var`: The environment variable name that should contain the API key

**Example:**
```python
from llm_nexus.exceptions import MissingAPIKeyError

try:
    from llm_nexus import llm_basic, llm_advanced
except MissingAPIKeyError as e:
    print(f"Missing API key for {e.provider}")
    print(f"Please set {e.env_var} environment variable")
```

### `NoneLLMError`

Raised when no LLM provider can be initialized after trying all available providers.

This exception is raised when:
- All API keys are missing
- All initialization attempts fail
- No valid LLM models could be created

**Example:**
```python
from llm_nexus.exceptions import NoneLLMError

try:
    from llm_nexus import llm_basic, llm_advanced
except NoneLLMError as e:
    print("Could not initialize any LLM provider")
    print(str(e))  # Shows helpful message about which API keys to set
```

## Usage Examples

### Basic Error Handling

```python
try:
    from llm_nexus import llm_basic, llm_advanced, LLM_MODEL_INSTANCE

    # Use your models
    response = llm_basic.invoke("Hello!")

except NoneLLMError:
    print("No LLM provider available. Please configure at least one API key:")
    print("  - GOOGLE_APPLICATION_CREDENTIALS for Anthropic Vertex AI")
    print("  - ANTHROPIC_API_KEY for Anthropic")
    print("  - OPENAI_API_KEY for OpenAI")
    print("  - GROQ_API_KEY for Groq")
    print("  - HUGGINGFACE_API_KEY for HuggingFace")
```

### Handling Specific Provider Errors

```python
from llm_nexus.exceptions import MissingAPIKeyError, NoneLLMError

try:
    # Import specific provider
    from llm_nexus.open_ai import openai_basic, openai_advanced

except MissingAPIKeyError as e:
    if e.provider == "OpenAI":
        print(f"OpenAI API key not found. Set {e.env_var} environment variable.")
    else:
        print(f"Missing API key for {e.provider}")

except Exception as e:
    print(f"Error initializing provider: {e}")
```

### Graceful Fallback

```python
from llm_nexus.exceptions import MissingAPIKeyError, NoneLLMError

llm = None

# Try multiple providers with graceful fallback
try:
    from llm_nexus.anthropic_llm import anthropic_basic_model
    llm = anthropic_basic_model
except MissingAPIKeyError:
    pass

if llm is None:
    try:
        from llm_nexus.open_ai import openai_basic
        llm = openai_basic
    except MissingAPIKeyError:
        pass

if llm is None:
    try:
        from llm_nexus.groq import groq_basic
        llm = groq_basic
    except MissingAPIKeyError:
        pass

if llm is None:
    raise NoneLLMError("No LLM provider could be initialized")

# Use llm
response = llm.invoke("Hello!")
```

## Environment Variables

The following environment variables are checked by llm-nexus:

| Provider | Environment Variable | Notes |
|----------|---------------------|-------|
| Anthropic Vertex AI | `GOOGLE_APPLICATION_CREDENTIALS` | Path to JSON credentials file |
| Anthropic | `ANTHROPIC_API_KEY` | API key from console.anthropic.com |
| OpenAI | `OPENAI_API_KEY` | API key from platform.openai.com |
| Groq | `GROQ_API_KEY` | API key from console.groq.com |
| HuggingFace | `HUGGINGFACE_API_KEY` | API key from huggingface.co |

## Initialization Flow

llm-nexus tries to initialize providers in this order:

1. Anthropic Vertex AI (if `GOOGLE_APPLICATION_CREDENTIALS` exists)
2. Anthropic (if `ANTHROPIC_API_KEY` is set)
3. OpenAI (if `OPENAI_API_KEY` is set)
4. Groq (if `GROQ_API_KEY` is set)
5. HuggingFace (if `HUGGINGFACE_API_KEY` is set)

If none of the providers can be initialized, a `NoneLLMError` is raised.
