# 🎯 Central de Atendimento Automática com IA

Uma solução completa de atendimento ao cliente, automatizada com IA, capaz de processar múltiplos canais (site, WhatsApp, e-mail) e resolver solicitações automaticamente ou encaminhar para análise humana.

**Desenvolvido para o Hackathon Microsoft Innovation Challenge - Novembro 2025**

---

## 📋 Sumário
- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação Local](#instalação-local)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Deploy na Azure](#deploy-na-azure)
- [API Endpoints](#api-endpoints)
- [Estrutura de Projeto](#estrutura-de-projeto)
- [Tecnologias](#tecnologias)

---

## 🌟 Visão Geral

### Problema
Empresas recebem múltiplos canais de atendimento (site, WhatsApp, e-mail) e precisam de soluções escaláveis para:
- Processar solicitações 24/7
- Responder dúvidas frequentes automaticamente
- Classificar e priorizar chamados complexos
- Reduzir tempo de resposta e custos operacionais

### Solução
Um orquestrador multicanal que:
- ✅ Recebe solicitações de diversos canais  
- ✅ Classifica com IA em tempo real  
- ✅ Responde automaticamente dúvidas simples  
- ✅ Encaminha casos complexos para análise humana  
- ✅ Registra métricas e histórico completo

---

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────┐
│         Frontend (React/Dashboard)          │
│   (Simulação de múltiplos canais)           │
└──────────────┬──────────────────────────────┘
               │ HTTP POST
               ▼
┌─────────────────────────────────────────────┐
│    Azure App Service (FastAPI)              │
│    - API Gateway                            │
│    - Processamento de requisições           │
└──────────────┬──────────────────────────────┘
               │
      ┌────────┴──────────┐
      ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│  IA Classifier   │  │  PostgreSQL DB   │
│  (Classificação) │  │  (Tickets/Dados) │
└──────────────────┘  └──────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│   N8N (Orquestração/Workflows)      │
│   - Triagem automática              │
│   - Encaminhamento para humano      │
│   - Integrações externas            │
└─────────────────────────────────────┘
```

**Stack Técnico:**
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (Azure Database for PostgreSQL)
- **Cloud:** Azure App Service
- **Automação:** N8N (opcional, para workflows avançados)
- **IA/NLP:** Mock de classificação (integrável com Azure Cognitive Services)

---

## 📦 Pré-requisitos

- Python 3.10+
- pip ou Poetry
- Git
- Conta Azure (com acesso a criar recursos)
- PostgreSQL instalado localmente (opcional, para testes)

---

## 🚀 Instalação Local

### **Passo 1: Clone o repositório**
```
git clone https://github.com/Jcnok/central-atendimento-azure.git
cd central-atendimento-azure
```

### **Passo 2: Crie um ambiente virtual**
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### **Passo 3: Instale as dependências**
```
pip install -r requirements.txt
```

### **Passo 4: Configure as variáveis de ambiente**
```
cp .env.example .env
# Edite o arquivo .env com suas credenciais PostgreSQL
```

### **Passo 5: Execute as migrações (criar tabelas)**
```
python -c "from src.config.database import init_db; init_db()"
```

### **Passo 6: Inicie a aplicação**
```
python src/main.py
```

### **Passo 7: Acesse a documentação interativa**
```
http://localhost:8000/docs
```

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
# Database PostgreSQL (Azure ou local)
DATABASE_URL=postgresql://dbadmin:SEU_PASSWORD_AQUI@central-atendimento-db.postgres.database.azure.com:5432/central_atendimento_db

# Aplicação
APP_ENV=development
APP_DEBUG=True
APP_HOST=0.0.0.0
APP_PORT=8000

# Azure (opcional, para integração com serviços Azure)
AZURE_COGNITIVE_KEY=sua_chave_aqui
AZURE_COGNITIVE_ENDPOINT=https://seu-endpoint.cognitiveservices.azure.com/
```

---

## ☁️ Deploy na Azure

### **Opção 1: Deploy via Azure CLI (Recomendado)**

#### **1.1 Gere o requirements.txt**
```
pip freeze > requirements.txt
```

#### **1.2 Crie um Resource Group**
```
az group create --name central-atendimento-rg --location "Brazil South"
```

#### **1.3 Crie o App Service Plan (Free Tier)**
```
az appservice plan create \
  --name central-atendimento-plan \
  --resource-group central-atendimento-rg \
  --sku F1 \
  --is-linux
```

#### **1.4 Crie a Web App**
```
az webapp create \
  --resource-group central-atendimento-rg \
  --plan central-atendimento-plan \
  --name central-atendimento-api \
  --runtime "PYTHON|3.12"
```

#### **1.5 Configure o Startup Command**
```
az webapp config set \
  --resource-group central-atendimento-rg \
  --name central-atendimento-api \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app"
```

#### **1.6 Defina as variáveis de ambiente**
```
az webapp config appsettings set \
  --resource-group central-atendimento-rg \
  --name central-atendimento-api \
  --settings DATABASE_URL="postgresql://dbadmin:SenhaForte@2025@central-atendimento-db.postgres.database.azure.com:5432/central_atendimento_db"
```

#### **1.7 Deploy do código (via ZIP)**
```
# Crie um ZIP com o projeto
zip -r deploy.zip src/ requirements.txt .env

# Faça deploy
az webapp deployment source config-zip \
  --resource-group central-atendimento-rg \
  --name central-atendimento-api \
  --src-path deploy.zip
```

Sua API estará disponível em:
```
https://central-atendimento-api.azurewebsites.net
```

### **Opção 2: Deploy via GitHub Actions (Automático)**

Crie `.github/workflows/deploy.yml`:

```
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: central-atendimento-api
        publish-profile: ${{ secrets.AZURE_PUBLISHPROFILE }}
        package: .
```

---

## 📡 API Endpoints

### **Health Check**
- `GET /` - Verifica saúde da API
- `GET /health` - Health check simples

### **Clientes**
- `POST /clientes/` - Criar novo cliente
- `GET /clientes/{cliente_id}` - Obter cliente
- `GET /clientes/` - Listar clientes (com paginação)

**Exemplo de requisição:**
```
curl -X POST "http://localhost:8000/clientes/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com",
    "telefone": "11999999999",
    "canal_preferido": "whatsapp"
  }'
```

### **Chamados (Tickets)**
- `POST /chamados/` - Criar novo chamado (com IA automática!)
- `GET /chamados/{chamado_id}` - Obter chamado
- `GET /chamados/` - Listar chamados (com filtros)
- `PUT /chamados/{chamado_id}` - Atualizar status
- `GET /chamados/cliente/{cliente_id}` - Listar chamados por cliente

**Exemplo de requisição:**
```
curl -X POST "http://localhost:8000/chamados/" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "canal": "whatsapp",
    "mensagem": "Gostaria de uma segunda via do boleto"
  }'
```

**Resposta esperada:**
```
{
  "chamado_id": 1,
  "cliente_id": 1,
  "canal": "whatsapp",
  "resposta": "📄 Clique aqui para acessar suas faturas e segunda via de boletos.",
  "resolvido_automaticamente": true,
  "prioridade": "baixa",
  "encaminhado_para_humano": false,
  "data_criacao": "2025-11-12T20:45:30.123456"
}
```

### **Métricas**
- `GET /metricas/` - Métricas gerais
- `GET /metricas/por-canal` - Métricas por canal
- `GET /metricas/por-status` - Distribuição por status

**Exemplo de resposta:**
```
{
  "total_chamados": 42,
  "total_clientes": 15,
  "chamados_resolvidos_automaticamente": 35,
  "chamados_encaminhados_para_humano": 7,
  "taxa_resolucao_automatica": "83.3%",
  "tempo_medio_resposta_segundos": "< 1s"
}
```

---

## 📁 Estrutura de Projeto

```
central-atendimento-azure/
├── src/
│   ├── __init__.py
│   ├── main.py                    # App FastAPI principal
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py            # Conexão PostgreSQL + SQLAlchemy
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cliente.py             # ORM Cliente
│   │   ├── chamado.py             # ORM Chamado
│   │   └── metrica.py             # ORM Métrica
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── cliente.py             # Schemas Pydantic Cliente
│   │   └── chamado.py             # Schemas Pydantic Chamado
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── clientes.py            # Endpoints /clientes
│   │   ├── chamados.py            # Endpoints /chamados
│   │   └── metricas.py            # Endpoints /metricas
│   ├── services/
│   │   ├── __init__.py
│   │   └── ia_classifier.py       # Lógica de IA/Classificação
│   └── utils/
│       ├── __init__.py
│       └── logger.py              # Configuração de logging
├── tests/
│   ├── __init__.py
│   └── test_endpoints.py          # Testes unitários
├── db/
│   └── .gitkeep                   # Pasta para migrations (se needed)
├── .github/
│   └── workflows/
│       └── deploy.yml             # CI/CD GitHub Actions
├── requirements.txt               # Dependências Python
├── .env.example                   # Template de variáveis
├── .gitignore                     # Arquivos a ignorar
├── README.md                      # Este arquivo
└── startup.sh                     # Script de inicialização (opcional)
```

---

## 🧪 Testes

### **Executar testes**
```
pytest tests/ -v
```

### **Teste individual de endpoint**
```
# Criar cliente
curl -X POST "http://localhost:8000/clientes/" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Test","email":"test@example.com","telefone":"11999999999"}'

# Criar chamado
curl -X POST "http://localhost:8000/chamados/" \
  -H "Content-Type: application/json" \
  -d '{"cliente_id":1,"canal":"site","mensagem":"segunda via boleto"}'

# Ver métricas
curl "http://localhost:8000/metricas/"
```

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Descrição |
|-----------|--------|----------|
| Python | 3.10+ | Linguagem principal |
| FastAPI | 0.104+ | Framework web |
| SQLAlchemy | 2.0+ | ORM |
| PostgreSQL | 12+ | Banco de dados |
| Pydantic | 2.5+ | Validação de dados |
| Gunicorn | 21+ | WSGI Server |
| Uvicorn | 0.24+ | ASGI Server |
| Azure App Service | - | Hospedagem cloud |

---

## 🔗 Integrações Futuras

- [ ] **Azure Cognitive Services** para NLP avançado
- [ ] **N8N** para workflows customizados
- [ ] **WhatsApp Business API** para integração real
- [ ] **SendGrid** para e-mails automáticos
- [ ] **Slack** para notificações
- [ ] **Dashboard React** para visualização
- [ ] **Auth0** para autenticação

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja LICENSE para detalhes.

---

## 👨‍💻 Autor

**João Nok** - Desenvolvedor Full-stack | Azure | IA  
LinkedIn: [seu-linkedin]  
GitHub: [@Jcnok](https://github.com/Jcnok)

---

## ❓ FAQ

**P: Como integro com N8N?**  
R: Crie um webhook no N8N que recebe dados do endpoint POST `/chamados/` e executa automações customizadas.

**P: Posso usar SQLite em vez de PostgreSQL?**  
R: Sim, mas não é recomendado para produção. Altere `DATABASE_URL` em `.env` para `sqlite:///./db/central.db`.

**P: Como faço deploy sem Azure?**  
R: Use Heroku, Railway, Render ou qualquer host que suporte Python/FastAPI.

---

## 🚀 Roadmap

- v1.0: MVP com CRUD básico e IA mock ✅
- v1.1: Integração N8N
- v1.2: Dashboard React
- v1.3: Integração Azure Cognitive Services
- v2.0: Multi-tenant architecture

---

**Desenvolvido com ❤️ para o Hackathon Microsoft Innovation Challenge**
```

***

## **FASE 13: Arquivo de startup.sh (3 min)**

Crie `startup.sh`:

```bash
#!/bin/bash

# Script de inicialização para Azure App Service

echo "🚀 Iniciando Central de Atendimento Automática..."

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados