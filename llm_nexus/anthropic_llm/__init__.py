import logging
from os import getenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from .. import LLM_MODEL_INSTANCE

anthropic_basic_model_name = getenv("ANTHROPIC_BASIC_MODEL", "claude-haiku-4-5-20251001")
anthropic_advanced_model_name = getenv("ANTHROPIC_ADVANCED_MODEL", "claude-opus-4-1-20250805")

def initialize_anthropic_models():
    try:
        # Get API key from environment
        api_key = getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables. "
                "Please create a .env file with ANTHROPIC_API_KEY=your-key-here"
            )
        else:
            logging.info(f"Anthropic API key found in environment: {api_key[:10]}****")


        anthropic_basic_model = ChatAnthropic(
            model=anthropic_basic_model_name,
            temperature=0.2,
            timeout=None,
            max_retries=2,
            max_tokens=16384
            # api_key=api_key
        )

        anthropic_advanced_model = ChatAnthropic(
            model=anthropic_advanced_model_name,
            temperature=0.2,
            timeout=None,
            max_retries=2,
            max_tokens=16384
            # api_key=api_key
        )

        response = anthropic_basic_model.invoke([HumanMessage(
            content="Hello, Anthropic! This is a test. Please respond only: Anthropic is connected.")])
        if response and response.content:
            logging.info("Anthropic basic model response: " + response.content)
        else:
            anthropic_basic_model=None
            anthropic_advanced_model=None
            logging.error("Anthropic basic model test invocation failed.")
            
    except Exception as e:
        anthropic_basic_model=None
        anthropic_advanced_model=None
        logging.error(f"Error initializing Anthropic models: {e}")
    
    return anthropic_basic_model, anthropic_advanced_model

if not LLM_MODEL_INSTANCE.basic_model or not LLM_MODEL_INSTANCE.advanced_model:
    anthropic_basic_model, anthropic_advanced_model = initialize_anthropic_models()

    if anthropic_basic_model is None or anthropic_advanced_model is None:
        logging.warning("Anthropic LLMs are not fully initialized.")
    else:
        logging.info("Anthropic LLMs initialized successfully.")

def anthropic_token_counter(query: str, model: str) -> int:
    try:
        return anthropic_basic_model.get_num_tokens(text=query, model=model)
    except Exception:
        logging.error("Error getting Anthropic token count.")
        return 0
