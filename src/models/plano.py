from sqlalchemy import Column, Integer, String, Numeric, Text
from src.config.database import Base

class Plano(Base):
    __tablename__ = "planos"

    plano_id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    velocidade = Column(String(50)) # Ex: "500MB", "5G"
    preco = Column(Numeric(10, 2), nullable=False)
    tipo = Column(String(50), nullable=False) # "internet", "movel", "tv"
