from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from src.config.database import Base

class KnowledgeBaseItem(Base):
    __tablename__ = "knowledge_base_items"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    # Dimension 1536 is for text-embedding-3-small and ada-002
    embedding = Column(Vector(1536))

    def __repr__(self):
        return f"<KnowledgeBaseItem(id={self.id}, topic={self.topic})>"
