from typing import Dict, List, Optional
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import AsyncSessionLocal
from src.models.chamado import Chamado
from src.utils.protocolo import gerar_protocolo

class TechnicalService:
    # Mock Knowledge Base (Keep as static for now, could be vector DB later)
    KNOWLEDGE_BASE = {
        "internet": "Para problemas de internet, tente reiniciar o modem e aguarde 5 minutos. Se persistir, verifique se a luz PON está piscando.",
        "lentidao": "Lentidão pode ser causada por muitos dispositivos conectados. Tente desconectar alguns aparelhos ou reiniciar o roteador.",
        "senha": "Para alterar a senha do Wi-Fi, acesse o aplicativo da central do assinante ou o IP 192.168.1.1.",
        "tv": "Se a TV estiver sem sinal, verifique se o cabo HDMI está bem conectado e se o decodificador está ligado.",
        "telefone": "Sem tom de discagem? Verifique se o cabo telefônico está conectado na porta TEL1 do modem."
    }

    @staticmethod
    async def search_knowledge_base(query: str) -> List[Dict[str, str]]:
        """
        Busca artigos na base de conhecimento.
        """
        results = []
        query_lower = query.lower()
        
        for key, content in TechnicalService.KNOWLEDGE_BASE.items():
            if key in query_lower:
                results.append({"topic": key, "content": content})
        
        return results

    @staticmethod
    async def create_ticket(description: str, priority: str = "normal", cliente_id: Optional[int] = None) -> Dict[str, any]:
        """
        Cria um ticket de suporte real no banco de dados.
        """
        if not cliente_id:
            return {"error": "ID do cliente é obrigatório para criar um ticket."}

        async with AsyncSessionLocal() as session:
            try:
                protocolo = gerar_protocolo()
                chamado = Chamado(
                    protocolo=protocolo,
                    cliente_id=cliente_id,
                    canal="chat_ia",
                    mensagem=description,
                    status="aberto",
                    prioridade=priority,
                    categoria="tecnico",
                    resolucao=None,
                    data_fechamento=None
                )
                session.add(chamado)
                await session.commit()
                
                return {
                    "ticket_id": chamado.id,
                    "protocolo": protocolo,
                    "status": "aberto",
                    "priority": priority,
                    "description": description,
                    "estimated_wait_time": "4 horas"
                }
            except Exception as e:
                await session.rollback()
                return {"error": f"Erro ao criar ticket: {str(e)}"}

    @staticmethod
    async def check_system_status() -> Dict[str, str]:
        """
        Verifica status do sistema (Mock).
        """
        return {
            "internet_fiber": "operational",
            "tv_service": "operational",
            "phone_service": "operational",
            "customer_portal": "operational"
        }

    @staticmethod
    async def get_client_by_email(email: str) -> Optional[int]:
        """
        Busca o ID do cliente pelo email.
        """
        from sqlalchemy import select
        from src.models.cliente import Cliente
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Cliente).filter(Cliente.email == email))
            cliente = result.scalars().first()
            return cliente.id if cliente else None
