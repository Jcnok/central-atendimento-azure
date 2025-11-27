from typing import Dict, List, Optional
import uuid

class TechnicalService:
    # Mock Knowledge Base
    KNOWLEDGE_BASE = {
        "internet": "Para problemas de internet, tente reiniciar o modem e aguarde 5 minutos. Se persistir, verifique se a luz PON está piscando.",
        "lentidao": "Lentidão pode ser causada por muitos dispositivos conectados. Tente desconectar alguns aparelhos ou reiniciar o roteador.",
        "senha": "Para alterar a senha do Wi-Fi, acesse o aplicativo da central do assinante ou o IP 192.168.1.1.",
        "tv": "Se a TV estiver sem sinal, verifique se o cabo HDMI está bem conectado e se o decodificador está ligado.",
        "telefone": "Sem tom de discagem? Verifique se o cabo telefônico está conectado na porta TEL1 do modem."
    }

    @staticmethod
    def search_knowledge_base(query: str) -> List[Dict[str, str]]:
        """
        Busca artigos na base de conhecimento (Mock).
        """
        results = []
        query_lower = query.lower()
        
        for key, content in TechnicalService.KNOWLEDGE_BASE.items():
            if key in query_lower:
                results.append({"topic": key, "content": content})
        
        # Se não encontrar nada específico, retorna dicas gerais se a query for muito curta
        if not results and len(query) < 5:
             results.append({"topic": "geral", "content": "Por favor, descreva melhor o problema para que eu possa ajudar."})
             
        return results

    @staticmethod
    def create_ticket(description: str, priority: str = "normal") -> Dict[str, any]:
        """
        Cria um ticket de suporte (Mock).
        """
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        return {
            "ticket_id": ticket_id,
            "status": "aberto",
            "priority": priority,
            "description": description,
            "estimated_wait_time": "4 horas" if priority == "normal" else "1 hora"
        }

    @staticmethod
    def check_system_status() -> Dict[str, str]:
        """
        Verifica status do sistema (Mock).
        """
        return {
            "internet_fiber": "operational",
            "tv_service": "operational",
            "phone_service": "operational",
            "customer_portal": "operational"
        }
