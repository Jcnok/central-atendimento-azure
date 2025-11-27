from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from src.config.database import Base

class HistoricoAtendimento(Base):
    __tablename__ = "historico_atendimentos"

    historico_id = Column(Integer, primary_key=True, index=True)
    chamado_id = Column(Integer, ForeignKey("chamados.id"), nullable=False)
    atendente_id = Column(Integer, ForeignKey("atendentes.atendente_id"), nullable=True) # Null if AI
    data_atendimento = Column(DateTime, server_default=func.now())
    descricao = Column(Text, nullable=False)

    chamado = relationship("Chamado", backref="historico")
    atendente = relationship("Atendente")
