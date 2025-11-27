from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey, String
from sqlalchemy.orm import relationship
from src.config.database import Base

class Pagamento(Base):
    __tablename__ = "pagamentos"

    pagamento_id = Column(Integer, primary_key=True, index=True)
    fatura_id = Column(Integer, ForeignKey("faturas.fatura_id"), nullable=False)
    data_pagamento = Column(Date, nullable=False)
    valor_pago = Column(Numeric(10, 2), nullable=False)
    forma_pagamento = Column(String(50)) # "boleto", "cartao", "pix"

    fatura = relationship("Fatura", backref="pagamentos")
