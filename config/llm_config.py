"""
LLM configuration for OpenRouter API.
Uses the free model for testing.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found. Please set it in .env file or environment variable.\n"
        "Create a .env file with: OPENROUTER_API_KEY=your-api-key-here"
    )

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-oss-120b:free"


def get_openai_client() -> OpenAI:
    """
    Get OpenAI client configured for OpenRouter.
    
    Returns:
        Configured OpenAI client
    """
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )


def get_llm(model_name: str = None, temperature: float = 0.7):
    """
    Get LangChain ChatOpenAI instance for agent use.
    
    Args:
        model_name: Model name (defaults to free model)
        temperature: Temperature for generation
        
    Returns:
        ChatOpenAI instance configured for OpenRouter
    """
    from langchain_openai import ChatOpenAI
    
    model = model_name or MODEL_NAME
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        max_retries=3,
    )

