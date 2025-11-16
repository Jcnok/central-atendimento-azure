# 🎯 Central de Atendimento Automática com IA

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma API de back-end robusta para uma central de atendimento, capaz de processar solicitações de múltiplos canais com classificação e resposta por IA.

**Desenvolvido para o Hackathon Microsoft Innovation Challenge - Novembro 2025**

---

## 📋 Sumário
- [Visão Geral](#-visão-geral)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Começando](#-começando)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Testes](#-testes)
- [Documentação da API](#-documentação-da-api)
- [Deploy na Azure](#-deploy-na-azure)
- [Roadmap](#-roadmap)
- [Licença e Contato](#-licença-e-contato)

---

## 🌟 Visão Geral

Este projeto oferece uma solução escalável para empresas que lidam com um alto volume de solicitações de clientes em diversos canais (site, WhatsApp, e-mail).

#### O Problema

-   Processamento manual e lento de solicitações.
-   Dificuldade em oferecer suporte 24/7.
-   Custos operacionais elevados com atendimento humano para dúvidas repetitivas.

#### A Solução

Um orquestrador de atendimento que automatiza o fluxo de trabalho:
-   ✅ **Recebe** solicitações de múltiplos canais.
-   ✅ **Classifica** a intenção do cliente com IA em tempo real.
-   ✅ **Responde** automaticamente a dúvidas frequentes (ex: segunda via de boleto).
-   ✅ **Encaminha** casos complexos e priorizados para análise humana.
-   ✅ **Gera métricas** sobre os atendimentos para análise de performance.

---

## 🛠️ Tecnologias

| Área | Tecnologia | Versão/Descrição |
| :--- | :--- | :--- |
| **Linguagem** | Python | 3.10+ |
| **Framework Web** | FastAPI | ASGI, alta performance |
| **Banco de Dados** | PostgreSQL | Banco de dados relacional |
| **ORM** | SQLAlchemy | v2.0, para manipulação de dados segura|
| **Validação**| Pydantic | v2, para validação e configurações |
| **Servidor** | Uvicorn & Gunicorn| Servidores ASGI/WSGI para dev/prod |
| **Testes** | Pytest | Testes automatizados com BD em memória |
| **Cloud** | Azure App Service | Hospedagem da aplicação |

---

## 🏗️ Arquitetura

A arquitetura segue um padrão de camadas desacoplado, facilitando a manutenção e a escalabilidade.

```
┌──────────────────────────────────┐
│         Canais de Entrada        │
│    (Frontend, WhatsApp, etc.)    │
└──────────────┬───────────────────┘
               │ HTTP POST
               ▼
┌──────────────────────────────────┐
│     Azure App Service (FastAPI)  │
│     - API Gateway                │
│     - Lógica de Negócio          │
└──────────────┬───────────────────┘
      ┌────────┴─────────┐
      ▼                  ▼
┌────────────────┐   ┌─────────────────┐
│ IA Classifier  │   │   PostgreSQL DB │
│ (Classificação)│   │  (Azure/Local)  │
└────────────────┘   └─────────────────┘
```
---

## 🚀 Começando

Siga os passos abaixo para ter o projeto rodando localmente em poucos minutos.

#### 1. Pré-requisitos

-   [Python 3.10+](https://www.python.org/)
-   [Git](https://git-scm.com/)
-   Um servidor PostgreSQL rodando (localmente ou na nuvem).

#### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/Jcnok/central-atendimento-azure.git
cd central-atendimento-azure

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

#### 3. Configuração

```bash
# Copie o arquivo de exemplo de variáveis de ambiente
cp .env.example .env

# Edite o arquivo .env e configure sua DATABASE_URL
# Exemplo para banco local:
# DATABASE_URL=postgresql://user:password@localhost:5432/nome_do_banco
```

#### 4. Execução

```bash
# Inicie a aplicação em modo de desenvolvimento
uvicorn src.main:app --reload
```

A aplicação estará disponível em `http://127.0.0.1:8000`.

**Nota:** As tabelas do banco de dados são criadas automaticamente na inicialização da aplicação. O comando manual `init_db()` não é mais necessário.

---

## 🔐 Autenticação

O acesso à API é protegido por **JSON Web Tokens (JWT)**. Todas as requisições para endpoints protegidos devem incluir um `token` de acesso no cabeçalho `Authorization`.

#### Fluxo de Autenticação:
1.  **Cadastro (`/auth/signup`):** Um novo usuário é criado com `username`, `email` e `password`.
2.  **Login (`/auth/login`):** O usuário envia `username` e `password` para obter um `access_token`.
3.  **Acesso a Endpoints Protegidos:** O `access_token` é enviado no cabeçalho das requisições:
    `Authorization: Bearer <seu_token_aqui>`

---

## ⚙️ Variáveis de Ambiente

As configurações da aplicação são gerenciadas via variáveis de ambiente através de um arquivo `.env`.

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| **`DATABASE_URL`** | **(Obrigatório)** String de conexão com o PostgreSQL. | `postgresql://user:pass@host:port/db` |
| **`SECRET_KEY`** | **(Obrigatório)** Chave secreta para assinar os tokens JWT. | `uma_chave_super_secreta` |
| `ALGORITHM` | Algoritmo de assinatura do token JWT. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token de acesso. | `30` |
| `APP_ENV` | Ambiente da aplicação. | `development` |
| `APP_DEBUG` | Ativa o modo debug. | `False` |
| `APP_HOST` | Host para o servidor Uvicorn. | `0.0.0.0` |
| `APP_PORT` | Porta para o servidor Uvicorn. | `8000` |

---

## 📁 Estrutura do Projeto

A estrutura do código é organizada por responsabilidades para facilitar a manutenção.

```
central-atendimento-azure/
├── src/
│   ├── main.py                # Ponto de entrada da aplicação FastAPI e Lifespan
│   ├── config/
│   │   ├── database.py        # Configuração da engine e sessão SQLAlchemy
│   │   └── settings.py        # Configurações Pydantic (carregadas do .env)
│   ├── models/                # Modelos ORM do SQLAlchemy (tabelas)
│   ├── schemas/               # Schemas Pydantic (validação de dados da API)
│   ├── routes/                # Endpoints da API (rotas)
│   └── services/              # Lógica de negócio (ex: classificação com IA)
├── tests/
│   └── test_endpoints.py      # Testes de integração com BD em memória
├── .github/
│   └── workflows/
│       └── deploy.yml         # Exemplo de workflow de CI/CD para Azure
├── requirements.in            # Dependências diretas do projeto
├── requirements.txt           # Dependências travadas (gerado por pip-tools)
├── pyproject.toml             # Configuração de ferramentas (Black, Ruff)
└── .env.example               # Arquivo de exemplo para variáveis de ambiente
```

---

## 🧪 Testes

O projeto utiliza **Pytest** para testes automatizados. Os testes rodam em um banco de dados **SQLite em memória**, garantindo que sejam rápidos e não afetem os dados de desenvolvimento.

Para executar a suíte de testes:

```bash
pytest
```

---

## 📡 Documentação da API

Este projeto utiliza os recursos de documentação automática do FastAPI. Ao iniciar a aplicação, duas interfaces de documentação interativa ficam disponíveis:

-   **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
-   **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Essas interfaces são a **fonte primária de verdade** para todos os endpoints, schemas e exemplos de uso.

<details>
<summary>Clique para ver um resumo dos endpoints principais</summary>

-   `POST /auth/signup`: Cria um novo usuário.
-   `POST /auth/login`: Autentica um usuário e retorna um token JWT.
-   `GET /`: Health check da API.
-   `POST /clientes/`: (Protegido) Cria um novo cliente.
-   `GET /clientes/{id}`: (Protegido) Obtém um cliente específico.
-   `POST /chamados/`: (Protegido) Cria um novo chamado.
-   `GET /chamados/{id}`: (Protegido) Obtém um chamado específico.
-   `GET /metricas/`: (Protegido) Obtém métricas gerais de atendimento.

</details>

---

## ☁️ Deploy na Azure

O projeto está pronto para deploy no **Azure App Service**.

#### Comando de Inicialização para Produção

O App Service deve ser configurado com o seguinte comando de inicialização:
```
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

---

## 📈 Roadmap

-   [x] **v1.1**: Autenticação JWT implementada.
-   [ ] **v1.2**: Integração com N8N para workflows, Dashboard em React.
-   [ ] **v1.3**: Integração real com **Azure Cognitive Services**, WhatsApp Business API, SendGrid.
-   [ ] **v2.0**: Arquitetura multi-tenant, ML para priorização, integração com CRMs.

---

## 📝 Licença e Contato

Este projeto está sob a licença MIT.

Desenvolvido por **Julio Okuda**.
-   **LinkedIn:** [linkedin.com/in/juliookuda](https://www.linkedin.com/in/juliookuda/)
-   **GitHub:** [@Jcnok](https://github.com/Jcnok)