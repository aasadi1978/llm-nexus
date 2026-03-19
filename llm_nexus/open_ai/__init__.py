from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import logging
from os import getenv
from pydantic import Field

openai_basic_model_name = getenv("OPENAI_BASIC_MODEL", "gpt-4o-mini")
openai_advanced_model_name = getenv("OPENAI_ADVANCED_MODEL", "gpt-5")
API_KEY = getenv('OPENAI_API_KEY')

class ChatOpenAIExtended(ChatOpenAI):
    model: str = Field(default='unknown', exclude=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.get('model', 'unknown')

def setup_openai_llms(http_client=None, http_async_client=None):
    """Initialize LLM models based on available OPENAI_API keys if available."""
    basic_llm, advanced_llm = None, None

    if API_KEY:

        logging.info(f"OPENAI API key found in environment: {API_KEY[:10]}****")
        try:
            if http_client and http_async_client:
                basic_llm = ChatOpenAIExtended(
                    model=openai_basic_model_name,
                    api_key=API_KEY,
                    http_client=http_client,
                    http_async_client=http_async_client
                )
            else:
                basic_llm = ChatOpenAIExtended(
                    model=openai_basic_model_name,
                    api_key=API_KEY
                )
            
            if basic_llm is not None:

                logging.info("Testing OpenAI basic model...")
                response = basic_llm.invoke([HumanMessage(
                    content="Hello, OpenAI! This is test. Please respond only the following: OpenAI is Connected!")])
                
                logging.info(f"OpenAI basic model response: {response.content}")
            
            else:
                return None, None

        except Exception as e:
            logging.error(f"Error invoking OpenAI: basic_llm: {e}")
            basic_llm = None

        try:
            if http_client and http_async_client:
                advanced_llm = ChatOpenAIExtended(
                    model=openai_advanced_model_name,
                    api_key=API_KEY,
                    http_client=http_client,
                    http_async_client=http_async_client
                )
            else:
                advanced_llm = ChatOpenAIExtended(
                    model=openai_advanced_model_name,
                    api_key=API_KEY
                )

        except Exception as e:
            logging.error(f"Error invoking OpenAI: advanced_llm: {e}")
            advanced_llm = None
            basic_llm = None
    
    else:
        logging.warning("OPENAI_API_KEY not found in environment variables.")

    if basic_llm:
        setattr(basic_llm, 'model', openai_basic_model_name)
    if advanced_llm:
        setattr(advanced_llm, 'model', openai_advanced_model_name)

    return basic_llm, advanced_llm

openai_basic, openai_advanced = setup_openai_llms()

def openai_token_counter(model: str, **kwargs) -> int:
    try:
        if 'query' in kwargs:
            message = kwargs['query']
        elif 'messages' in kwargs:
            message = kwargs['messages']
        else:
            logging.error("No 'query' or 'messages' found in kwargs for token counting.")
            return 0

        return openai_basic.get_num_tokens(text=message, model=model, **kwargs)
    except Exception:
        logging.error("Error getting OpenAI token count.")
        return 0