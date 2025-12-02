from typing import Dict, List, Optional
from sqlalchemy import select
from src.config.database import AsyncSessionLocal
from src.models.plano import Plano
from src.models.cliente import Cliente
from src.models.contrato import Contrato
from src.models.fatura import Fatura
from src.models.chamado import Chamado
from src.utils.protocolo import gerar_protocolo
from src.utils.security import get_password_hash
from datetime import date, timedelta, datetime
import random

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

    @staticmethod
    async def list_plans() -> List[Dict[str, any]]:
        """Lista todos os planos disponíveis no banco."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Plano))
            planos = result.scalars().all()
            return [
                {
                    "nome": p.nome,
                    "velocidade": p.velocidade,
                    "preco": float(p.preco),
                    "tipo": p.tipo,
                    "descricao": p.descricao
                }
                for p in planos
            ]

    @staticmethod
    async def compare_plans(plan_name_a: str, plan_name_b: str) -> str:
        """Compara dois planos lado a lado."""
        async with AsyncSessionLocal() as session:
            # Helper para busca fuzzy
            async def get_plan(name):
                result = await session.execute(select(Plano).filter(Plano.nome.ilike(f"%{name}%")))
                return result.scalars().first()

            p1 = await get_plan(plan_name_a)
            p2 = await get_plan(plan_name_b)

            if not p1 or not p2:
                return "Não encontrei um dos planos para comparação. Tente usar nomes como 'Fibra 500MB' ou 'Móvel 5G'."

            diff_price = float(p2.preco) - float(p1.preco)
            
            comparison = f"**Comparação: {p1.nome} vs {p2.nome}**\n\n"
            comparison += f"*   **{p1.nome}**: {p1.velocidade} por R$ {float(p1.preco):.2f} - {p1.descricao}\n"
            comparison += f"*   **{p2.nome}**: {p2.velocidade} por R$ {float(p2.preco):.2f} - {p2.descricao}\n\n"
            
            if diff_price > 0:
                comparison += f"O plano **{p2.nome}** custa R$ {diff_price:.2f} a mais."
            elif diff_price < 0:
                comparison += f"O plano **{p2.nome}** é R$ {abs(diff_price):.2f} mais barato."
            else:
                comparison += "Ambos têm o mesmo preço."
                
            return comparison

    @staticmethod
    async def get_invoice_by_email(email: str) -> str:
        """Busca 2ª via de fatura pendente pelo e-mail (sem login)."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Cliente).filter(Cliente.email == email))
            cliente = result.scalars().first()
            
            if not cliente:
                return "Não encontrei nenhum cliente com este e-mail. Deseja contratar um plano?"

            # Busca última fatura pendente
            result_fatura = await session.execute(
                select(Fatura)
                .join(Contrato)
                .filter(Contrato.cliente_id == cliente.id, Fatura.status == 'pendente')
                .order_by(Fatura.data_vencimento.asc())
            )
            fatura = result_fatura.scalars().first()
            
            if not fatura:
                return "Você não possui faturas pendentes no momento! 🎉"

            link = f"https://central.com/faturas/{fatura.fatura_id}.pdf"
            return f"Encontrei sua fatura vencendo em {fatura.data_vencimento.strftime('%d/%m/%Y')} no valor de R$ {float(fatura.valor):.2f}. \n\n📥 **Baixe aqui:** [2ª Via do Boleto]({link})\n\nCódigo de barras: 34191.79001 01043.510047 91020.150008 8"

    @staticmethod
    def troubleshoot_internet() -> str:
        """Retorna guia estático de troubleshooting."""
        return """**Guia de Solução de Problemas - Internet Lenta ou Sem Sinal** 🛠️

1.  **Reinicie o Modem**: Desligue da tomada, espere 30 segundos e ligue novamente. Aguarde as luzes estabilizarem (aprox. 2 min).
2.  **Verifique os Cabos**: Garanta que o cabo de fibra (ponta amarela ou verde) esteja bem conectado e não esteja dobrado.
3.  **Teste no Cabo**: Se possível, conecte um computador via cabo de rede para descartar problemas no Wi-Fi.
4.  **Luzes do Modem**:
    *   **PON (Verde Fixa)**: Sinal chegando corretamente.
    *   **LOS (Vermelha)**: Rompimento de fibra. Contate o suporte técnico.
    *   **Wi-Fi (Piscando)**: Rede sem fio ativa.

Se o problema persistir e a luz LOS estiver vermelha, por favor, peça para falar com o **Suporte Técnico**."""

    @staticmethod
    async def simulate_sale(nome: str, email: str, plano_nome: str) -> str:
        """Simula uma venda criando cliente, contrato e fatura."""
        async with AsyncSessionLocal() as session:
            try:
                # 1. Find Plan
                result_plano = await session.execute(select(Plano).filter(Plano.nome.ilike(f"%{plano_nome}%")))
                plano = result_plano.scalars().first()
                
                if not plano:
                    return f"Desculpe, não encontrei o plano '{plano_nome}'. Temos: Fibra 500MB, Fibra 1GB, Móvel 5G."

                # 2. Check if client exists
                result_cliente = await session.execute(select(Cliente).filter(Cliente.email == email))
                existing_client = result_cliente.scalars().first()
                
                if existing_client:
                    return "Já existe um cliente com este e-mail. Por favor, faça login para contratar novas linhas."

                # 3. Create Client
                novo_cliente = Cliente(
                    nome=nome,
                    email=email,
                    hashed_password=get_password_hash("123mudar"), # Default password
                    telefone="11999999999", # Placeholder
                    endereco="Endereço não informado",
                    canal_preferido="chat_ia"
                )
                session.add(novo_cliente)
                await session.flush() # Get ID

                # 4. Create Contract
                contrato = Contrato(
                    cliente_id=novo_cliente.id,
                    plano_id=plano.plano_id,
                    data_inicio=date.today(),
                    status="ativo",
                    tipo_servico=plano.tipo
                )
                session.add(contrato)
                await session.flush()

                # 5. Create Invoice
                fatura = Fatura(
                    contrato_id=contrato.contrato_id,
                    data_emissao=date.today(),
                    data_vencimento=date.today() + timedelta(days=5),
                    valor=plano.preco,
                    status="pendente"
                )
                session.add(fatura)
                
                await session.commit()
                
                return f"""🎉 **Parabéns, {nome}!** Contratação realizada com sucesso!
                
**Plano:** {plano.nome} ({plano.velocidade})
**Valor:** R$ {float(plano.preco):.2f}/mês
**Instalação:** Agendada para amanhã, horário comercial.

Seu boleto de adesão já foi gerado: [Boleto]({fatura.fatura_id}.pdf).
Sua senha provisória de acesso ao portal é: `123mudar`."""

            except Exception as e:
                await session.rollback()
                return f"Erro ao processar contratação: {str(e)}"
