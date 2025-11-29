import logging
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import AzureChatOpenAI
from src.config.settings import settings

logger = logging.getLogger(__name__)

class SQLAgent:
    def __init__(self, db_session=None):
        """
        Inicializa o agente SQL usando LangChain.
        
        Args:
            db_session: Sessão do banco de dados (não usado diretamente pelo LangChain, 
                       mas mantido para compatibilidade se necessário).
                       O LangChain usa sua própria conexão via SQLDatabase.
        """
        # Configuração do banco de dados para LangChain
        # O LangChain precisa da URL de conexão síncrona (psycopg2)
        # Convertemos a URL async (postgresql+asyncpg) para sync (postgresql) se necessário
        # E garantimos que sslmode=require esteja presente para Azure PostgreSQL
        db_url = str(settings.DATABASE_URL).replace("postgresql+asyncpg://", "postgresql://")
        if "sslmode" not in db_url:
             if "?" in db_url:
                 db_url += "&sslmode=require"
             else:
                 db_url += "?sslmode=require"
        
        self.db = SQLDatabase.from_uri(db_url)
        
        # Configuração do LLM (Azure OpenAI)
        deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_GPT4O
        
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_KEY:
            error_msg = "Azure OpenAI Endpoint ou Key não configurados no .env"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        logger.info(f"🔌 Configurando Azure OpenAI com deployment: {deployment_name}")
        logger.info(f"🌐 Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
        
        try:
            self.llm = AzureChatOpenAI(
                azure_deployment=deployment_name,
                openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_KEY,
                temperature=0,
                verbose=True
            )
            
            # Criação do agente SQL
            self.agent_executor = create_sql_agent(
                llm=self.llm,
                db=self.db,
                agent_type="openai-tools",
                verbose=True,
                handle_parsing_errors=True
            )
            logger.info("✅ Agente SQL inicializado com sucesso.")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Agente SQL: {str(e)}")
            # Fallback ou re-raise dependendo da estratégia. Aqui vamos re-raise para alertar.
            raise e

    async def process_query(self, query: str) -> str:
        """
        Processa uma pergunta em linguagem natural e retorna a resposta baseada no banco de dados.
        """
        try:
            logger.info(f"🤖 SQL Agent processando pergunta: {query}")
            
            # O agente do LangChain executa de forma síncrona por padrão, 
            # mas podemos usar ainvoke para async
            response = await self.agent_executor.ainvoke({"input": query})
            
            output = response.get("output", "Não consegui encontrar uma resposta para sua pergunta.")
            
            logger.info(f"✅ Resposta do agente: {output}")
            return output
            
        except Exception as e:
            logger.error(f"❌ Erro CRÍTICO no SQL Agent: {str(e)}", exc_info=True)
            return f"Erro técnico detalhado: {str(e)}"
