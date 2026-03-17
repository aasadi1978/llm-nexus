import logging
from os import getenv
from pathlib import Path
import sys
from .llm import LLMModel

llm_basic = None
llm_advanced = None
get_token_count_init = None

google_credentials_key_path = Path(getenv("GOOGLE_APPLICATION_CREDENTIALS")).resolve()
if google_credentials_key_path.exists():
    logging.info("GOOGLE_APPLICATION_CREDENTIALS found. Attempting to initialize Anthropic claude models ...")
    from .anthropic_vertex import (anthropic_vertex_basic_model as llm_basic,
                                anthropic_vertex_advanced_model as llm_advanced,
                                anthropic_vertex_advanced_model_name as llm_advanced_name,
                                anthropic_vertex_basic_model_name as llm_basic_name)

    from .anthropic_vertex.token_counter_vertex import count_tokens as get_token_count_init


if llm_basic is None or llm_advanced is None:
    if getenv("ANTHROPIC_API_KEY"):
        from .anthropic_llm import (anthropic_basic_model as llm_basic,
                                    anthropic_advanced_model as llm_advanced,
                                    anthropic_advanced_model_name as llm_advanced_name,
                                    anthropic_basic_model_name as llm_basic_name)

        from .anthropic_llm.token_counter import count_tokens as get_token_count_init

if llm_basic is None or llm_advanced is None:
    if getenv("OPENAI_API_KEY"):
        from .open_ai import (openai_basic as llm_basic,
                                    openai_advanced as llm_advanced,
                                    openai_advanced_model_name as llm_advanced_name,
                                    openai_basic_model_name as llm_basic_name)

        from .open_ai import openai_token_counter as get_token_count_init

if llm_basic is None or llm_advanced is None:
    if getenv("GROQ_API_KEY"):
        from .groq import (groq_basic as llm_basic,
                                groq_advanced as llm_advanced,
                                groq_advanced_model_name as llm_advanced_name,
                                groq_basic_model_name as llm_basic_name)

        from .groq import groq_token_counter as get_token_count_init

if llm_basic is None or llm_advanced is None:
    if getenv("HUGGINGFACE_API_KEY"):
        from .huggingface import (huggingface_basic as llm_basic, huggingface_advanced as llm_advanced,
                                        huggingface_basic_model_name as llm_basic_name,
                                        huggingface_advanced_model_name as llm_advanced_name)

        from .huggingface import huggingface_token_counter as get_token_count_init

if llm_basic is None or llm_advanced is None:
    logging.error("No LLM models have been initialized. Please set up the required API keys.")
    sys.exit(1)

get_token_count = get_token_count_init
LLM_MODEL_INSTANCE = LLMModel.get_instance()
LLM_MODEL_INSTANCE.initialize(basic_model=llm_basic, advanced_model=llm_advanced)
logging.info(f"Basic Model: {llm_basic_name}, Advanced Model: {llm_advanced_name}")
