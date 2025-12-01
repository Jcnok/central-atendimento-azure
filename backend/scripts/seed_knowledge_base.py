import asyncio
import os
import sys

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.rag_service import RAGService
from src.config.database import init_db

async def seed():
    print("🚀 Iniciando população da Base de Conhecimento...")
    
    # Garante que as tabelas existam
    await init_db()
    
    kb_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")
    
    if not os.path.exists(kb_dir):
        print(f"❌ Diretório {kb_dir} não encontrado.")
        return

    files = [f for f in os.listdir(kb_dir) if f.endswith(".txt")]
    
    for filename in files:
        topic = filename.replace(".txt", "").replace("_", " ").title()
        filepath = os.path.join(kb_dir, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        print(f"📚 Processando: {topic}...")
        result = await RAGService.add_document(topic, content)
        
        if "error" in result:
            print(f"❌ Erro ao adicionar {topic}: {result['error']}")
        else:
            print(f"✅ {topic} adicionado com sucesso (ID: {result['id']})")

    print("✨ Concluído!")

if __name__ == "__main__":
    asyncio.run(seed())
