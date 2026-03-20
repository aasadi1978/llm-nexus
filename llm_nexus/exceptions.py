"""Custom exceptions for the llm-nexus package."""


class MissingAPIKeyError(Exception):
    """
    Raised when no API key is found for a specific LLM provider.

    This exception is raised when attempting to initialize an LLM provider
    but the required API key is not found in environment variables.
    """

    def __init__(self, provider: str, env_var: str = None):
        self.provider = provider
        self.env_var = env_var

        if env_var:
            message = (
                f"Missing API key for {provider}. "
                f"Please set the {env_var} environment variable."
            )
        else:
            message = f"Missing API key for {provider}."

        super().__init__(message)


class NoneLLMError(Exception):
    """
    Raised when no LLM provider can be initialized.

    This exception is raised after attempting to initialize all available
    LLM providers (Anthropic Vertex, Anthropic, OpenAI, Groq, HuggingFace)
    and none of them could be successfully initialized due to missing API
    keys or initialization failures.
    """

    def __init__(self, message: str = None):
        if message is None:
            message = (
                "No LLM models could be initialized. "
                "Please set up at least one of the following API keys:\n"
                "  - GOOGLE_APPLICATION_CREDENTIALS (for Anthropic Vertex)\n"
                "  - ANTHROPIC_API_KEY (for Anthropic)\n"
                "  - OPENAI_API_KEY (for OpenAI)\n"
                "  - GROQ_API_KEY (for Groq)\n"
                "  - HUGGINGFACE_API_KEY (for HuggingFace)"
            )

        super().__init__(message)
