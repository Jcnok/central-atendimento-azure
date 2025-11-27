from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.config.database import Base
import enum

class StatusContratoEnum(str, enum.Enum):
    ativo = "ativo"
    cancelado = "cancelado"
    suspenso = "suspenso"

class Contrato(Base):
    __tablename__ = "contratos"

    contrato_id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    plano_id = Column(Integer, ForeignKey("planos.plano_id"), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date)
    status = Column(Enum(StatusContratoEnum), default=StatusContratoEnum.ativo)
    tipo_servico = Column(String(50)) # Redundant with Plano.tipo but good for quick access

    cliente = relationship("Cliente", backref="contratos")
    plano = relationship("Plano")
