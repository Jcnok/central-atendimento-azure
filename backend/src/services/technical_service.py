from typing import Dict, List, Optional
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import AsyncSessionLocal
from src.models.chamado import Chamado
from src.utils.protocolo import gerar_protocolo

class TechnicalService:
    # Mock Knowledge Base (Keep as static for now, could be vector DB later)
    # KNOWLEDGE_BASE removed in favor of RAGService

    @staticmethod
    async def search_knowledge_base(query: str) -> List[Dict[str, str]]:
        """
        Busca artigos na base de conhecimento.
        """
        from src.services.rag_service import RAGService
        return await RAGService.search(query)

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
            return cliente.id if cliente else None

    @staticmethod
    async def get_open_tickets(client_id: int) -> List[Dict[str, any]]:
        """
        Busca tickets abertos do cliente.
        """
        from sqlalchemy import select, or_
        
        async with AsyncSessionLocal() as session:
            # Busca tickets com status 'aberto' ou 'em_andamento'
            result = await session.execute(
                select(Chamado).filter(
                    Chamado.cliente_id == client_id,
                    or_(Chamado.status == "aberto", Chamado.status == "em_andamento")
                )
            )
            chamados = result.scalars().all()
            
            return [
                {
                    "ticket_id": c.id,
                    "protocolo": c.protocolo,
                    "status": c.status,
                    "priority": c.prioridade,
                    "description": c.mensagem,
                    "created_at": c.data_criacao.isoformat() if c.data_criacao else None
                }
                for c in chamados
            ]

    @staticmethod
    async def update_ticket(ticket_id: int, status: Optional[str] = None, priority: Optional[str] = None, note: Optional[str] = None) -> Dict[str, any]:
        """
        Atualiza um ticket existente.
        """
        async with AsyncSessionLocal() as session:
            try:
                chamado = await session.get(Chamado, ticket_id)
                if not chamado:
                    return {"error": "Ticket não encontrado."}
                
                updates = []
                if status:
                    chamado.status = status
                    updates.append(f"Status alterado para {status}")
                
                if priority:
                    chamado.prioridade = priority
                    updates.append(f"Prioridade alterada para {priority}")
                
                if note:
                    # Adiciona nota à mensagem ou cria um campo de histórico se existisse
                    # Por enquanto, vamos anexar à mensagem para simplificar, ou apenas retornar que foi anotado
                    # Idealmente teríamos uma tabela de interações/comentários
                    chamado.mensagem += f"\n\n[Atualização]: {note}"
                    updates.append("Nota adicionada")

                if status == "resolvido":
                    from datetime import datetime
                    chamado.data_fechamento = datetime.now()
                    chamado.resolucao = note or "Resolvido via Chat IA"

                await session.commit()
                
                return {
                    "success": True,
                    "ticket_id": ticket_id,
                    "updates": updates,
                    "current_status": chamado.status
                }
            except Exception as e:
                await session.rollback()
                return {"error": f"Erro ao atualizar ticket: {str(e)}"}
