from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.config.database import Base
import enum

class StatusFaturaEnum(str, enum.Enum):
    pendente = "pendente"
    pago = "pago"
    atrasado = "atrasado"
    cancelado = "cancelado"

class Fatura(Base):
    __tablename__ = "faturas"

    fatura_id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("contratos.contrato_id"), nullable=False)
    data_emissao = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(StatusFaturaEnum), default=StatusFaturaEnum.pendente)

    contrato = relationship("Contrato", backref="faturas")
