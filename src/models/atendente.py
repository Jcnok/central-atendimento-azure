from sqlalchemy import Column, Integer, String, Enum
from src.config.database import Base
import enum

class EspecialidadeEnum(str, enum.Enum):
    tecnico = "tecnico"
    financeiro = "financeiro"
    vendas = "vendas"
    geral = "geral"

class Atendente(Base):
    __tablename__ = "atendentes"

    atendente_id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telefone = Column(String(20))
    especialidade = Column(Enum(EspecialidadeEnum), default=EspecialidadeEnum.geral)
