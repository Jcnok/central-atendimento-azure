import asyncio
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.sql_agent import SQLAgent
from src.config.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("🚀 Iniciando teste do SQL Agent...")
    
    try:
        agent = SQLAgent()
        query = "Quantos clientes temos?"
        
        print(f"\n❓ Pergunta: {query}")
        response = await agent.process_query(query)
        print(f"\n✅ Resposta: {response}")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
