from openai import AsyncAzureOpenAI
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    def __init__(self):
        if not settings.AZURE_OPENAI_KEY or not settings.AZURE_OPENAI_ENDPOINT:
            logger.warning("Azure OpenAI credentials not found. Service will fail if used.")
            self.client = None
        else:
            self.client = AsyncAzureOpenAI(
                api_key=settings.AZURE_OPENAI_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
            )
            self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_GPT4O

    async def get_chat_response(self, messages: list, temperature: float = 0.7) -> str:
        if not self.client:
            return "Error: Azure OpenAI not configured."
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Azure OpenAI: {e}")
            raise e
