from langchain_openai import OpenAIEmbeddings
import logging
from os import getenv
from ..config import AI_CONFIG

def create_openai_embedding(
    model_name: str = "text-embedding-3-small",
    http_client: any = None,
    http_async_client: any = None
) -> OpenAIEmbeddings:
    """
    Create an OpenAI Embedding model instance.

    Args:
        model_name (str): The name of the OpenAI embedding model to use.
        http_client: Optional HTTP client for requests.
        http_async_client: Optional async HTTP client for requests.

    Returns:
        OpenAIEmbeddings: An instance of OpenAIEmbeddings.
    
    Note:
        OpenAI's text-embedding-3 models return normalized embeddings by default.
    """
    api_key = getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("OPENAI_API_KEY not found in environment variables.")
        return None
    try:

        if http_client and http_async_client:
            embedding_model = OpenAIEmbeddings(
                model=model_name,
                api_key=api_key,
                http_client=http_client,
                http_async_client=http_async_client
            )
        else:
            embedding_model = OpenAIEmbeddings(
                model=model_name,
                api_key=api_key
            )
        logging.info(f"Created OpenAI Embedding model: {model_name}")
        return embedding_model
    
    except Exception as e:
        AI_CONFIG.log_exception("Error creating OpenAI Embedding model.")
        return None

def create_openai_embedding_model():

    openai_embedding = create_openai_embedding()
    if openai_embedding is None:
        logging.info("OpenAI Embedding model is not available. Trying with http clients..." )
        http_client = AI_CONFIG.get_http_client()
        async_http_client = AI_CONFIG.get_async_http_client()

        if http_client and async_http_client:
            openai_embedding = create_openai_embedding(
                http_client=http_client,
                http_async_client=async_http_client
            )

        if openai_embedding is None:
            logging.error("Failed to initialize OpenAI Embedding model.")

    return openai_embedding