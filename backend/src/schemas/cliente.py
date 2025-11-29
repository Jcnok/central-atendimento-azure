from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr
    password: str
    telefone: Optional[str] = None
    canal_preferido: str = "site"


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    canal_preferido: Optional[str] = None


class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: Optional[str]
    canal_preferido: str
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
