import logging
from os import getenv
from anthropic import AnthropicVertex
from typing import Dict, List, Union
from langchain_core.messages import AnyMessage
from langchain_core.documents import Document
from .. import get_token_count

def count_tokens(
        model: str,
        messages: Union[List[Dict[str, str]], List[AnyMessage], List[Document]], 
        system: str = "",
        tools: List[Dict[str, str]] = []
        ) -> int:
    
    """
    Count tokens in messages for AnthropicVertex models.
    
    Args:
        messages: List of message dicts OR LangGraph AnyMessage objects OR LangChain Document objects
        system: System message for context
        tools: List of tool descriptions for context
        
    Returns:
        int: Total token count
    """

    # Handle empty messages
    if not messages:
        return 0
    
    # Use the provided system prompt, or empty string for minimal token counting
    if not system:
        system = ""

    # Attempt to use the imported get_token_count function
    combined_content = " ".join(
        msg.content if isinstance(msg, AnyMessage) else msg['content'] 
        for msg in messages
    )

    if get_token_count is not None:
        try:
            return get_token_count(query=combined_content, model=model)
        except Exception as e:
            logging.warning(f"get_token_count failed, falling back to Anthropic client: {e}")

    try: 
        # Initialize Anthropic client
        anthropic_client = AnthropicVertex(region=getenv("ANTHROPIC_VERTEX_LOCATION", "europe-west1"))
        # Detect input type and convert to required format
        first_item = messages[0]
        
        if isinstance(first_item, Document):
            # For Document objects, count tokens in page_content
            # Create a single user message with all document content
            combined_content = "\n\n".join(doc.page_content for doc in messages)
            formatted_messages = [{"role": "user", "content": combined_content}]
            
        elif isinstance(first_item, dict):
            # Already in correct format
            formatted_messages = messages
            
        elif hasattr(first_item, "type") and hasattr(first_item, "content"):
            # Convert AnyMessage objects (HumanMessage, AIMessage, etc.)
            formatted_messages = [
                {
                    "role": "assistant" if msg.type == "ai" else msg.type,
                    "content": msg.content
                }
                for msg in messages
            ]
        else:
            raise ValueError(f"Unsupported message type: {type(first_item)}")
        
        response = anthropic_client.messages.count_tokens(
            model=model if model else "claude-3-5-sonnet@20240620",
            system=system or "",
            tools=tools or [],
            messages=formatted_messages,
        )
        return response.input_tokens
        
    except Exception:
        logging.error("Error counting tokens with Anthropic.")
        return 0