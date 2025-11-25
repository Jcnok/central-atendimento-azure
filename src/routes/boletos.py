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
    # Simulação: Se o email conter "erro", falha
    if "erro" in dados.email.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum boleto pendente encontrado para este email.",
        )

    return BoletoResponse(
        mensagem="2ª Via gerada com sucesso",
        codigo_barras="34191.79001 01043.510047 91020.150008 8 91230000015000",
        link_pdf="https://example.com/boleto-simulado.pdf",
        valor=150.00,
        vencimento="30/12/2025",
    )
