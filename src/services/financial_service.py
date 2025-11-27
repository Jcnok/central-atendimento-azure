from typing import Dict, List, Optional

class FinancialService:
    @staticmethod
    def gerar_boleto_simulado(email: str, cpf: Optional[str] = None) -> Optional[Dict[str, any]]:
        """
        Gera uma 2ª via de boleto simulada.
        Retorna None se não encontrar boleto pendente.
        """
        # Simulação: Se o email conter "erro", falha
        if "erro" in email.lower():
            return None

        return {
            "mensagem": "2ª Via gerada com sucesso",
            "codigo_barras": "34191.79001 01043.510047 91020.150008 8 91230000015000",
            "link_pdf": "https://example.com/boleto-simulado.pdf",
            "valor": 150.00,
            "vencimento": "30/12/2025",
        }

    @staticmethod
    def check_payment_status(boleto_id: str) -> str:
        """
        Verifica o status de um pagamento.
        """
        # Mock implementation
        return "pago" if "123" in boleto_id else "pendente"

    @staticmethod
    def get_invoices(cliente_id: int) -> List[Dict[str, any]]:
        """
        Retorna lista de faturas.
        """
        # Mock implementation
        return [
            {"id": "FAT-001", "valor": 150.00, "status": "paga", "vencimento": "2025-10-30"},
            {"id": "FAT-002", "valor": 150.00, "status": "pendente", "vencimento": "2025-11-30"},
        ]
