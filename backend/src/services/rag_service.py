import logging
from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector
from openai import AsyncAzureOpenAI

from src.config.database import AsyncSessionLocal
from src.config.settings import settings
from src.models.knowledge_base import KnowledgeBaseItem

logger = logging.getLogger(__name__)

class RAGService:
    
    @staticmethod
    def _get_client():
        return AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )

    @staticmethod
    async def generate_embedding(text: str) -> List[float]:
        """
        Gera embedding usando Azure OpenAI.
        """
        client = RAGService._get_client()
        try:
            response = await client.embeddings.create(
                input=text,
                model=settings.AZURE_OPENAI_DEPLOYMENT_EMBEDDING
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise

    @staticmethod
    async def add_document(topic: str, content: str) -> Dict[str, any]:
        """
        Adiciona um documento à base de conhecimento.
        """
        try:
            # Gera embedding do conteúdo (ou tópico + conteúdo)
            text_to_embed = f"{topic}: {content}"
            embedding = await RAGService.generate_embedding(text_to_embed)
            
            async with AsyncSessionLocal() as session:
                item = KnowledgeBaseItem(
                    topic=topic,
                    content=content,
                    embedding=embedding
                )
                session.add(item)
                await session.commit()
                return {"success": True, "id": item.id, "topic": topic}
        except Exception as e:
            logger.error(f"Erro ao adicionar documento: {e}")
            return {"error": str(e)}

    @staticmethod
    async def search(query: str, limit: int = 3) -> List[Dict[str, str]]:
        """
        Busca documentos relevantes usando similaridade de cosseno.
        """
        try:
            query_embedding = await RAGService.generate_embedding(query)
            
            async with AsyncSessionLocal() as session:
                # Busca usando o operador de distância L2 (<->) ou similaridade de cosseno (<=>)
                # pgvector recomenda <=> para cosseno (quanto menor, mais similar se normalizado, mas aqui é distância de cosseno)
                # Na verdade, para cosine similarity, usamos <=> e ordenamos.
                
                result = await session.execute(
                    select(KnowledgeBaseItem)
                    .order_by(KnowledgeBaseItem.embedding.cosine_distance(query_embedding))
                    .limit(limit)
                )
                items = result.scalars().all()
                
                return [
                    {"topic": item.topic, "content": item.content}
                    for item in items
                ]
        except Exception as e:
            logger.error(f"Erro na busca RAG: {e}")
            return []
