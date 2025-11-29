from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/boletos", tags=["Boletos"])


class BoletoRequest(BaseModel):
    email: EmailStr
    cpf: str | None = None


class BoletoResponse(BaseModel):
    mensagem: str
    codigo_barras: str
    link_pdf: str
    valor: float
    vencimento: str


@router.post("/gerar", response_model=BoletoResponse)
async def gerar_boleto(dados: BoletoRequest):
    """
    Gera uma 2ª via de boleto simulada.
    Em um cenário real, integraria com um gateway de pagamento.
    """
    from src.services.financial_service import FinancialService
    
    resultado = FinancialService.gerar_boleto_simulado(dados.email, dados.cpf)
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum boleto pendente encontrado para este email.",
        )

    return BoletoResponse(**resultado)
