
from sqlalchemy import Column, DateTime, Integer, String, func, Text

from src.config.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    telefone = Column(String(20))
    endereco = Column(Text)
    canal_preferido = Column(String(50), default="site")
    data_criacao = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Cliente(id={self.id}, email={self.email})>"
