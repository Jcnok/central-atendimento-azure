from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    canal_preferido: str = "site"

class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: Optional[str]
    canal_preferido: str
    data_criacao: datetime
    
    class Config:
        from_attributes = True
