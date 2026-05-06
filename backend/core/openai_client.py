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

if _api_key:
    # Detect if it's a Groq key
    if _api_key.startswith("gsk_"):
        _base_url = "https://api.groq.com/openai/v1"
        _model_name = "llama-3.3-70b-versatile"
        logger.info(f"Groq key detected. Forcing Groq base URL and model: {_model_name}")

    client = AsyncOpenAI(
        api_key=_api_key,
        base_url=_base_url
    )
    logger.info(f"OpenAI-compatible client initialized | model: {_model_name}")
else:
    client = None
    logger.warning("No LLM API Key found in environment variables")


class OpenAIService:
    """Service for LLM API operations (now using Grok via xAI)."""
    
    def __init__(self, client):
        self.client = client
        self.model_name = _model_name
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Note: xAI/Grok may not support embeddings. This method is kept for compatibility
        but may need to be updated or use a different embedding service.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector
        """
        if not self.client:
            raise ValueError("LLM API Key not configured")
        
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}. Returning dummy vector for demo.")
            # Return a zero vector of the expected dimension (1536)
            return [0.0] * 1536
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
        
        Returns:
            List of embedding vectors
        """
        if not self.client:
            raise ValueError("LLM API Key not configured")
        
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.warning(f"Batch embedding generation failed: {e}. Returning dummy vectors for demo.")
            return [[0.0] * 1536 for _ in texts]
    
    async def chat_completion(
        self,
        messages: List[dict],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        Generate chat completion using Grok (xAI).
        
        Args:
            messages: Chat messages
            stream: Whether to stream response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Chat completion (or async generator if streaming)
        """
        if not self.client:
            raise ValueError("XAI_API_KEY not configured")
        
        logger.info(f"LLM chat completion | messages_count: {len(messages)} | stream: {stream}")
        
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=stream,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if stream:
            return response
        result = response.choices[0].message.content
        logger.info(f"LLM chat completion completed | response_length: {len(result)}")
        return result
    
    async def transcribe_audio(self, audio_file_path: str, language: str = "en") -> str:
        """
        Transcribe audio file using Whisper.
        
        Note: xAI/Grok may not support Whisper. This method may need to use OpenAI directly.
        
        Args:
            audio_file_path: Path to audio file
            language: Language code
        
        Returns:
            Transcribed text
        """
        if not self.client:
            raise ValueError("XAI_API_KEY not configured")
        
        with open(audio_file_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )
        return transcript.text
    
    async def summarize_text(self, text: str, max_length: int = 500) -> str:
        """
        Summarize text using Grok.
        
        Args:
            text: Input text
            max_length: Maximum summary length
        
        Returns:
            Summary text
        """
        messages = [
            {
                "role": "system",
                "content": f"Summarize the following text concisely (max {max_length} words):"
            },
            {
                "role": "user",
                "content": text
            }
        ]
        
        summary = await self.chat_completion(messages, temperature=0.3)
        return summary


openai_service = OpenAIService(client)
