from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship
from src.config.database import Base


class Chamado(Base):
    __tablename__ = "chamados"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    canal = Column(String(50), nullable=False)  # "site", "whatsapp", "email"
    mensagem = Column(Text, nullable=False)
    status = Column(
        String(50), default="aberto"
    )  # "aberto", "resolvido", "encaminhado"
    resposta_automatica = Column(Text)
    encaminhado_para_humano = Column(Boolean, default=False)
    data_criacao = Column(DateTime, server_default=func.now())
    data_atualizacao = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="chamados")

    def __repr__(self):
        return f"<Chamado(id={self.id}, cliente_id={self.cliente_id}, status={self.status})>"
