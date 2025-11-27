from typing import Dict, List, Optional

class GeneralService:
    # Mock FAQ
    FAQ = {
        "horario": "Nosso atendimento funciona 24 horas por dia, 7 dias por semana.",
        "localizacao": "Nossa sede fica na Av. Paulista, 1000, São Paulo - SP.",
        "contato": "Você pode entrar em contato pelo telefone 0800-123-4567 ou pelo email contato@empresa.com.br.",
        "cancelamento": "Para cancelar, entre em contato com o setor de retenção pelo 0800-123-4567, opção 5.",
        "contratacao": "Você pode contratar novos planos diretamente pelo nosso site ou app."
    }

    @staticmethod
    def search_faq(query: str) -> List[Dict[str, str]]:
        """
        Busca na FAQ (Mock).
        """
        results = []
        query_lower = query.lower()
        
        for key, content in GeneralService.FAQ.items():
            if key in query_lower:
                results.append({"topic": key, "content": content})
        
        if not results:
             # Fallback simples
             if "ajuda" in query_lower:
                 results.append({"topic": "ajuda", "content": "Posso ajudar com dúvidas sobre horários, localização, contato e planos."})
                 
        return results

    @staticmethod
    def get_company_info(topic: str) -> str:
        """
        Retorna informações institucionais.
        """
        topic_lower = topic.lower()
        if "horario" in topic_lower or "horas" in topic_lower:
            return GeneralService.FAQ["horario"]
        elif "endereco" in topic_lower or "local" in topic_lower:
            return GeneralService.FAQ["localizacao"]
        elif "telefone" in topic_lower or "email" in topic_lower or "contato" in topic_lower:
            return GeneralService.FAQ["contato"]
        
        return "Desculpe, não tenho essa informação específica. Tente perguntar sobre horários, endereço ou contato."
