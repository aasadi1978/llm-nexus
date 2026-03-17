from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage
import logging
from os import getenv
from pydantic import Field
from utils.ssl_verification import bypass_ssl_verification

bypass_ssl_verification() 

huggingface_basic_model_name = getenv("HUGGINGFACE_BASIC_MODEL", "Qwen/Qwen3.5-35B-A3B")
huggingface_advanced_model_name = getenv("HUGGINGFACE_ADVANCED_MODEL", "Qwen/Qwen3.5-35B-A3B")
API_KEY = getenv('HUGGINGFACE_API_KEY')

class ChatHuggingFaceExtended(ChatHuggingFace):
    model: str = Field(default='unknown', exclude=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Extract model name from llm parameter if it's an endpoint
        if hasattr(self, 'llm') and hasattr(self.llm, 'repo_id'):
            self.model = self.llm.repo_id
        else:
            self.model = kwargs.get('model', 'unknown')

def setup_huggingface_llms(http_client=None, http_async_client=None):
    """Initialize HuggingFace LLM models based on available HUGGINGFACE_API_KEY if available."""
    basic_llm, advanced_llm = None, None

    if API_KEY:

        logging.info(f"HUGGINGFACE API key found in environment: {API_KEY[:10]}****")
        try:
            # Create HuggingFaceEndpoint first, then wrap with ChatHuggingFace
            endpoint = HuggingFaceEndpoint(
                repo_id=huggingface_basic_model_name,
                huggingfacehub_api_token=API_KEY,
                temperature=0.7,
                max_new_tokens=512,
                top_p=0.95
            )

            # Wrap endpoint with ChatHuggingFace for chat interface
            basic_llm = ChatHuggingFaceExtended(llm=endpoint)

            if basic_llm is not None:

                logging.info("Testing HuggingFace basic model...")
                response = basic_llm.invoke([HumanMessage(
                    content="Hello, Qwen! This is test. Please respond only the following: Qwen is Connected!"
                )])

                logging.info(f"HuggingFace basic model response: {response.content}")

            else:
                return None, None

        except Exception as e:
            logging.error(f"Error invoking HuggingFace: basic_llm: {e}")
            basic_llm = None

        try:
            # Advanced model (same as basic for now since we're using the same model)
            endpoint_advanced = HuggingFaceEndpoint(
                repo_id=huggingface_advanced_model_name,
                huggingfacehub_api_token=API_KEY,
                temperature=0.7,
                max_new_tokens=512,
                top_p=0.95
            )

            advanced_llm = ChatHuggingFaceExtended(llm=endpoint_advanced)
            if advanced_llm is not None:
                logging.info("Testing HuggingFace advanced model...")
                response_adv = advanced_llm.invoke([HumanMessage(
                    content="Hello, Qwen! This is a test for the advanced model. Please respond only the following: Qwen advanced is Connected!"
                )])
                logging.info(f"HuggingFace advanced model response: {response_adv.content}")

        except Exception as e:
            logging.error(f"Error invoking HuggingFace: advanced_llm: {e}")
            advanced_llm = None
            basic_llm = None

    else:
        logging.warning("HUGGINGFACE_API_KEY not found in environment variables.")

    if basic_llm:
        setattr(basic_llm, 'model', huggingface_basic_model_name)
    if advanced_llm:
        setattr(advanced_llm, 'model', huggingface_advanced_model_name)

    return basic_llm, advanced_llm

huggingface_basic, huggingface_advanced = setup_huggingface_llms()

def hello_qwen():
    """Simple example: call Qwen model with greeting."""
    basic_llm, _ = setup_huggingface_llms()

    if basic_llm:
        response = basic_llm.invoke([HumanMessage(content="Hello Qwen! Introduce yourself in one sentence.")])
        logging.info(f"Qwen says: {response.content}")
        print(f"Qwen says: {response.content}")
        return response.content
    else:
        logging.error("Failed to initialize Qwen model")
        print("Failed to initialize Qwen model")
        return None

def huggingface_token_counter(query: str, model: str) -> int:
    """Placeholder for token counting - HuggingFace doesn't have built-in token counter like OpenAI."""
    try:
        # Basic estimation: ~4 characters per token (rough approximation)
        return len(query) // 4
    except Exception:
        logging.error("Error estimating HuggingFace token count.")
        return 0
