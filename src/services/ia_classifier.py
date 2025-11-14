"""
Serviço de classificação e resposta automática com IA (mock)
Aqui você integra com Azure Cognitive Services, N8N, ou LLM de sua escolha
"""


class IAClassifier:
    @staticmethod
    def classificar(mensagem: str, canal: str) -> dict:
        """
        Classifica a mensagem e decide se pode resolver automaticamente
        """
        mensagem_lower = mensagem.lower()

        # Classificação baseada em palavras-chave
        if any(
            palavra in mensagem_lower
            for palavra in ["segunda via", "boleto", "fatura", "invoice"]
        ):
            return {
                "intencao": "documento",
                "resposta": "📄 Clique aqui para acessar suas faturas e segunda via de boletos.",
                "resolvido": True,
                "prioridade": "baixa",
            }

        elif any(
            palavra in mensagem_lower
            for palavra in ["meu plano", "upgrade", "downgrade", "trocar plano"]
        ):
            return {
                "intencao": "gerenciamento_plano",
                "resposta": "📋 Para gerenciar seu plano, acesse 'Minha Conta' no menu principal.",
                "resolvido": True,
                "prioridade": "média",
            }

        elif any(
            palavra in mensagem_lower
            for palavra in [
                "problema",
                "erro",
                "não funciona",
                "bugado",
                "travado",
                "urgente",
            ]
        ):
            return {
                "intencao": "problema_tecnico",
                "resposta": "⚠️ Seu chamado foi registrado como prioritário. Um especialista entrará em contato em breve.",
                "resolvido": False,
                "prioridade": "alta",
            }

        elif any(
            palavra in mensagem_lower
            for palavra in ["obrigado", "valeu", "thanks", "tks"]
        ):
            return {
                "intencao": "agradecimento",
                "resposta": "😊 De nada! Fico feliz em ajudar. Qualquer dúvida, estarei aqui.",
                "resolvido": True,
                "prioridade": "baixa",
            }

        else:
            return {
                "intencao": "geral",
                "resposta": "👋 Obrigado pelo contato! Seu chamado foi registrado. Responderemos em breve.",
                "resolvido": False,
                "prioridade": "média",
            }
