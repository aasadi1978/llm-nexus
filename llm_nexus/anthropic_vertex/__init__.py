from pathlib import Path
import logging
from os import getenv
from .initialize_anthropic_vertex_models import configure_anthropic_vertex_chat
from ..exceptions import MissingAPIKeyError


if not Path(getenv("GOOGLE_APPLICATION_CREDENTIALS")).resolve().exists():
    raise MissingAPIKeyError("Anthropic Vertex AI", "GOOGLE_APPLICATION_CREDENTIALS")

else:
    anthropic_vertex_basic_model, anthropic_vertex_advanced_model, anthropic_vertex_basic_model_name, anthropic_vertex_advanced_model_name = configure_anthropic_vertex_chat()
    if anthropic_vertex_basic_model is None or anthropic_vertex_advanced_model is None:
        logging.warning("Anthropic Vertex LLMs are not fully initialized.")
    else:
        logging.info("Anthropic Vertex LLMs initialized successfully.")
        logging.info(f"Basic Model: {anthropic_vertex_basic_model.model}, Advanced Model: {anthropic_vertex_advanced_model.model}")
        