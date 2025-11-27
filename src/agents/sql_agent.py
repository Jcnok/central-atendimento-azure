import logging
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.openai_service import AzureOpenAIService

logger = logging.getLogger(__name__)

class SQLAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = AzureOpenAIService()
        
    async def process_query(self, user_query: str) -> str:
        """
        Translates natural language to SQL, executes it, and summarizes results.
        """
        # 1. Generate SQL
        schema_summary = """
        Tables:
        - clientes (id, nome, email, telefone, endereco, canal_preferido)
        - contratos (contrato_id, cliente_id, plano_id, status, tipo_servico)
        - planos (plano_id, nome, preco, tipo)
        - faturas (fatura_id, contrato_id, valor, status, data_vencimento)
        - chamados (id, protocolo, cliente_id, status, prioridade, categoria, mensagem)
        """
        
        system_prompt = f"""
        You are a SQL Expert for a Telecom company.
        Your goal is to answer user questions by generating a SQL query based on the schema below.
        
        {schema_summary}
        
        Rules:
        1. Return ONLY the SQL query. No markdown, no explanations.
        2. ONLY generate SELECT queries. NEVER UPDATE, DELETE, or DROP.
        3. Use PostgreSQL syntax.
        4. If the question cannot be answered with SQL, return "ERROR: Cannot answer".
        """
        
        try:
            sql_query = await self.llm.get_chat_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ]
            )
            
            sql_query = sql_query.strip().replace("```sql", "").replace("```", "")
            
            if "SELECT" not in sql_query.upper():
                 return "Desculpe, só posso realizar consultas de leitura (SELECT)."

            logger.info(f"Generated SQL: {sql_query}")
            
            # 2. Execute SQL
            result = await self.db.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
            
            data = [dict(zip(columns, row)) for row in rows]
            
            # 3. Summarize Results
            summary_prompt = f"""
            User Question: {user_query}
            SQL Result: {json.dumps(data, default=str)}
            
            Please summarize the answer in a natural, professional way for an Admin Dashboard.
            Format as a concise text or bullet points.
            """
            
            summary = await self.llm.get_chat_response(
                messages=[{"role": "user", "content": summary_prompt}]
            )
            
            return summary

        except Exception as e:
            logger.error(f"SQL Agent Error: {e}")
            return "Desculpe, ocorreu um erro ao processar sua consulta."
