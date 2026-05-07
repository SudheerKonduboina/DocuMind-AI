import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Optional
from backend.core.logger import logger

# Load environment variables
load_dotenv()

# Initialize OpenAI client with xAI configuration
_api_key = os.getenv("XAI_API_KEY")
_base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
_model_name = os.getenv("MODEL_NAME", "grok-2-latest")

# Create async client instance
if _api_key:
    client = AsyncOpenAI(api_key=_api_key, base_url=_base_url)
    logger.info(f"LLM client initialized with model: {_model_name}")
else:
    client = None
    logger.warning("XAI_API_KEY not found in environment variables")


async def ask_llm(prompt: str) -> str:
    """
    Send a prompt to the LLM and return the text response.

    This is the single entry point for all LLM interactions in the application.
    Uses Grok (xAI) via OpenAI-compatible API.

    Args:
        prompt: The text prompt to send to the LLM

    Returns:
        str: The LLM's text response

    Raises:
        ValueError: If API key is not configured
        Exception: If the API call fails
    """
    if not client:
        raise ValueError(
            "XAI_API_KEY not configured. Please set XAI_API_KEY in environment variables."
        )

    try:
        logger.info(f"LLM request sent | prompt_length: {len(prompt)}")

        response = await client.chat.completions.create(
            model=_model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        result = response.choices[0].message.content
        logger.info(f"LLM response received | response_length: {len(result)}")

        return result

    except Exception as e:
        logger.error(f"LLM request failed | error: {str(e)}")
        raise


async def chat_completion(
    messages: List[dict],
    stream: bool = False,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
):
    """
    Generate chat completion (async, supports streaming).

    This function provides compatibility with the existing OpenAI service interface.

    Args:
        messages: Chat messages
        stream: Whether to stream response
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Chat completion (or async generator if streaming)

    Raises:
        ValueError: If API key is not configured
        Exception: If the API call fails
    """
    if not client:
        raise ValueError(
            "XAI_API_KEY not configured. Please set XAI_API_KEY in environment variables."
        )

    try:
        logger.info(
            f"LLM chat completion | messages_count: {len(messages)} | stream: {stream}"
        )

        response = await client.chat.completions.create(
            model=_model_name,
            messages=messages,
            stream=stream,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if stream:
            return response
        result = response.choices[0].message.content
        logger.info(f"LLM chat completion completed | response_length: {len(result)}")
        return result

    except Exception as e:
        logger.error(f"LLM chat completion failed | error: {str(e)}")
        raise
