import logging
from os import getenv
import sys
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from pydantic import Field
from .. import LLM_MODEL_INSTANCE
from ..config import AI_CONFIG

# Modeles: https://console.groq.com/docs/models
# which one should I use?

# Ultra-cheap & fast: llama-3.1-8b-instant
# Balanced high-quality: gpt-oss-20b or llama-3.3-70b-versatile
# Max quality: gpt-oss-120b
# Built-in tools / agents: groq/compound or groq/compound-mini
# Speech-to-text: whisper-large-v3(-turbo)
# Moderation: meta-llama/llama-guard-4-12b, or preview Prompt Guard / Safety GPT-OSS


groq_basic_model_name = getenv("GROQ_BASIC_MODEL", "llama-3.1-8b-instant")
groq_advanced_model_name = getenv("GROQ_ADVANCED_MODEL", "llama-3.1-8b-instant")

class ChatGroqExtended(ChatGroq):
    
    model: str = Field(default='unknown', exclude=True)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.get('model', 'unknown')


def initialize_groq_models(http_client=None, http_async_client=None):
    try:
        basic_llm, advanced_llm = None, None
        api_key = getenv("GROQ_API_KEY")

        if api_key:

            logging.info(f"GROQ API key found in environment: {api_key[:10]}****")
            if http_client and http_async_client:
                basic_llm = ChatGroqExtended(
                    api_key=api_key,
                    temperature=0.2,
                    http_client=http_client,
                    http_async_client=http_async_client,
                    model=groq_basic_model_name
                )
            else:
                basic_llm = ChatGroqExtended(
                    api_key=api_key,
                    model=groq_basic_model_name,
                    temperature=0.2,
                )

            if basic_llm:
            
                res = basic_llm.invoke([HumanMessage(content="Hello, Basic GROQ! This is a test message. Please respond only: GROQ is connected.")])
                if res and res.content:
                    logging.info(f"Basic GROQ LLM response received: {res.content}")
                else:
                    logging.error("No content received from Basic LLM invocation of GROQ.")
                    return None, None

            if http_client and http_async_client:
                advanced_llm = ChatGroqExtended(
                    api_key=api_key,
                    model=groq_advanced_model_name,
                    temperature=0.2,
                    http_client=http_client,
                    http_async_client=http_async_client 
                )
            else:
                advanced_llm = ChatGroqExtended(
                    api_key=api_key,
                    model=groq_advanced_model_name,
                    temperature=0.2,
                )

        else:
            logging.warning("GROQ_API_KEY not found in environment variables.")

    except Exception as e:
        logging.error(f"GROQ: Error invoking GROQ LLMs: {str(e)}")

        basic_llm = None
        advanced_llm = None

    return basic_llm, advanced_llm

if not LLM_MODEL_INSTANCE.basic_model or not LLM_MODEL_INSTANCE.advanced_model:
    logging.info("Initializing GROQ LLM models...")

    groq_basic, groq_advanced = initialize_groq_models()

    if groq_basic is None or groq_advanced is None:
        logging.warning("GROQ LLMs are not fully initialized. Trying with HTTP clients...")
        http_client = AI_CONFIG.get_http_client()
        async_http_client = AI_CONFIG.get_async_http_client()

        if http_client and async_http_client:
            groq_basic, groq_advanced = initialize_groq_models(http_client, async_http_client)

        if groq_basic is None or groq_advanced is None:
            logging.warning("GROQ LLMs are not fully initialized.")
            sys.exit(1)

def groq_token_counter(model: str, **kwargs) -> int:
    try:

        if 'query' in kwargs:
            message = kwargs['query']
        elif 'messages' in kwargs:
            message = kwargs['messages']
        else:
            logging.error("No 'query' or 'messages' found in kwargs for token counting.")
            return 0

        return groq_basic.get_num_tokens(text=message, model=model, **kwargs)
    except Exception:
        logging.error("Error getting GROQ token count.")
        return 0