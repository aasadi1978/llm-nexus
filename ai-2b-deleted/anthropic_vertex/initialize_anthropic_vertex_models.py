from langchain_core.messages import HumanMessage
from langchain_google_vertexai.model_garden import ChatAnthropicVertex
import logging
from os import getenv
from pathlib import Path

from pydantic import Field
from ..config import AI_CONFIG

class ChatAnthropicVertexExtended(ChatAnthropicVertex):
    """Extended ChatAnthropicVertex to customize behavior if needed."""

    model: str = Field(default='unknown', exclude=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model=kwargs.get("model_name", "unknown")

location = getenv("ANTHROPIC_VERTEX_LOCATION", "europe-west1")
project = getenv("GOOGLE_CLOUD_PROJECT", "fxei-meta-project")
max_tokens = int(getenv("ANTHROPIC_VERTEX_MAX_OUTPUT_TOKENS", "16384"))

anthropic_vertex_basic_model_name = getenv("ANTHROPIC_VERTEX_BASIC_MODEL", "claude-haiku-4-5@20251001")
# anthropic_vertex_advanced_model_name = getenv("ANTHROPIC_VERTEX_ADVANCED_MODEL", "claude-opus-4-5@20251101")
# anthropic_vertex_advanced_model_name = getenv("ANTHROPIC_VERTEX_ADVANCED_MODEL", "claude-sonnet-4-5@20250929")
anthropic_vertex_advanced_model_name = getenv("ANTHROPIC_VERTEX_ADVANCED_MODEL", "claude-opus-4-6@default")

def configure_anthropic_vertex_chat():
    try:
        # Get API key from environment
        credentials_key_path = Path(getenv("GOOGLE_APPLICATION_CREDENTIALS")).resolve()
        if not credentials_key_path.exists():
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS not found or the file does not exist. "
                "Please create a .env file with GOOGLE_APPLICATION_CREDENTIALS=path-to-your-key.json"
            )

        anthropic_vertex_basic_model = ChatAnthropicVertexExtended(
            project=project, location=location, model_name=anthropic_vertex_basic_model_name,
            max_output_tokens=max_tokens)

        anthropic_vertex_advanced_model = ChatAnthropicVertexExtended(
            project=project, location=location, model_name=anthropic_vertex_advanced_model_name,
            max_output_tokens=max_tokens)
        response = anthropic_vertex_basic_model.invoke([HumanMessage(
            content="Hello, Claude! This is a test. Please respond only: Claude is connected.")])

        if response and response.content:
            logging.info("Claude basic model response: " + response.content)
        else:
            anthropic_vertex_basic_model=None
            anthropic_vertex_advanced_model=None
            logging.error("Claude basic model test invocation failed.")
    except Exception:
        anthropic_vertex_basic_model=None
        anthropic_vertex_advanced_model=None
        AI_CONFIG.log_exception("Error initializing Claude models.")

    return anthropic_vertex_basic_model, anthropic_vertex_advanced_model, anthropic_vertex_basic_model_name, anthropic_vertex_advanced_model_name