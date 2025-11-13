from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    
    class Config:
        from_attributes = True
