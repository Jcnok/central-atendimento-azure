from sqlalchemy import Column, Integer, String, DateTime, func
from src.config.database import Base
from datetime import datetime

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefone = Column(String(20))
    canal_preferido = Column(String(50), default="site")
    data_criacao = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, email={self.email})>"
