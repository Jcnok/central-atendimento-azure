from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChamadoCreate(BaseModel):
    cliente_id: int
    canal: str
    mensagem: str


class ChamadoResponse(BaseModel):
    id: int
    cliente_id: int
    canal: str
    mensagem: str
    status: str
    resposta_automatica: Optional[str]
    encaminhado_para_humano: bool
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)


class ChamadoCreateResponse(BaseModel):
    """Schema de resposta para a criação de um novo chamado."""

    chamado_id: int
    cliente_id: int
    canal: str
    resposta: str
    resolvido_automaticamente: bool
    prioridade: str
    encaminhado_para_humano: bool
    data_criacao: datetime
