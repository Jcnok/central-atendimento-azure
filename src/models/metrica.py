from sqlalchemy import Column, Integer, DateTime, Float, func
from src.config.database import Base

class Metrica(Base):
    __tablename__ = "metricas"
    
    id = Column(Integer, primary_key=True, index=True)
    total_chamados = Column(Integer, default=0)
    chamados_automaticos = Column(Integer, default=0)
    chamados_encaminhados = Column(Integer, default=0)
    tempo_medio_resposta = Column(Float, default=0.0)
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Metrica(id={self.id}, total={self.total_chamados})>"
