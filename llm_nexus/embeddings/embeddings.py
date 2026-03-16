import logging
from os import getenv
from typing import Union

import vertexai
from vertexai.language_models import TextEmbeddingModel
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from .qwenvl_embedding_wrapper import QwenVLEmbeddingsWrapper
from .vertex_embedding_wrapper import VertexAIEmbeddingsWrapper
from ..config import AI_CONFIG

location = getenv("ANTHROPIC_VERTEX_LOCATION", "europe-west1")
project = getenv("GOOGLE_CLOUD_PROJECT", "fxei-meta-project")

AI_CONFIG.bypass_ssl_verification()


EMBEDDING_MODEL_TYPE = Union[GoogleGenerativeAIEmbeddings, OpenAIEmbeddings, VertexAIEmbeddingsWrapper, QwenVLEmbeddingsWrapper, Embeddings]

def get_multilingual_setting() -> bool:
    """Check if multilingual embedding model is requested via environment variable."""
    multilingual_env = getenv("MULTILINGUAL_EMBEDDING_MODEL", "false").lower()
    return multilingual_env in ("1", "true", "yes")

def get_qwen_vl_setting() -> bool:
    """Check if Qwen VL embedding model is requested via environment variable."""
    qwen_vl_env = getenv("USE_QWEN_VL_EMBEDDING", "false").lower()
    return qwen_vl_env in ("1", "true", "yes")

def get_embedding_model() -> EMBEDDING_MODEL_TYPE | None:

    """Initialize and return the appropriate embedding model based on configuration."""
    multilingual = get_multilingual_setting()
    use_qwen_vl = get_qwen_vl_setting()
    embedding_model = None

    # Try Qwen VL Embedding first if explicitly requested
    if use_qwen_vl:
        try:
            logging.info("Attempting to initialize Qwen VL Embedding model ...")
            device = getenv("QWEN_VL_DEVICE", "cpu")
            embedding_model = QwenVLEmbeddingsWrapper(
                model_name="Qwen/Qwen3-VL-Embedding-2B",
                device=device
            )
            test_vector = embedding_model.embed_query("hello, world!")
            if test_vector:
                logging.info("Using Qwen VL Embeddings as the embedding model.")
                return embedding_model
        except Exception as e:
            logging.warning(f"Qwen VL Embeddings initialization failed: {e}")
            embedding_model = None

        try:
            vertexai.init(project=project, location=location)
            vertex_model = TextEmbeddingModel.from_pretrained('gemini-embedding-001')
            vector = vertex_model.get_embeddings(texts=["Hello world", "How are you?"])

            if vector:
                # Wrap in LangChain-compatible adapter
                embedding_model = VertexAIEmbeddingsWrapper(vertex_model)
                logging.info(f"Using Google Generative AI Embeddings {vertex_model._model_id} as the embedding model.")

            return embedding_model

        except ImportError:
            embedding_model = None
            logging.warning("Vertex AI SDK not installed. Skipping Google Generative AI Embeddings initialization.")
        
        except Exception as e:
            logging.warning(f"Google Generative AI Embeddings initialization failed.")
            embedding_model = None
            
    if embedding_model is None:
        try:
            embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", api_key=getenv("GOOGLE_API_KEY"))
            vector = embedding_model.embed_query("hello, world!")
            if vector:
                logging.info("Using Google Generative AI Embeddings as the embedding model.")

                return embedding_model
            
        except Exception as e:
            logging.warning(f"Google Generative AI Embeddings initialization failed: {e}")
            embedding_model = None

    if embedding_model is None:
        
        logging.info("Attempting to initialize HuggingFace Embeddings model ...")
        from langchain_huggingface import HuggingFaceEmbeddings

        try:
            if multilingual:
                # Using multilingual embedding model for Chinese/English support
                logging.info("Using multilingual embedding model for Chinese/English support")
                embedding_model = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True},
                    multilingual= multilingual
                    ) or None
            else:
                # Default: English-only lightweight model
                embedding_model = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
            
            if embedding_model:
                test_vector = embedding_model.embed_query("hello, world!")
                if test_vector:
                    logging.info("Using HuggingFace Embeddings as the embedding model.")
                    return embedding_model
                
        except Exception as e:
            logging.warning(f"HuggingFace Embeddings initialization failed: {e}")
            embedding_model = None
                

    if embedding_model is None:
        from ..open_ai.openai_embedding import create_openai_embedding_model
        try:
            embedding_model = create_openai_embedding_model()
            if embedding_model:
                logging.info("Using OpenAI Embeddings as the embedding model.")

                test_vector = embedding_model.embed_query("hello, world!")
                if test_vector:
                    logging.info("Using OpenAI Embeddings as the embedding model.")
                    return embedding_model

        except Exception as e:
            logging.warning(f"OpenAI Embeddings initialization failed: {e}")
            embedding_model = None
        
    return embedding_model

EmbeddingModel: EMBEDDING_MODEL_TYPE = get_embedding_model()