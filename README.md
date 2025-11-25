# 🚀 Central de Atendimento Inteligente (Azure + AI)

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)
![Azure](https://img.shields.io/badge/Azure-App%20Service-0078D4?logo=microsoftazure)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma plataforma completa de **Orquestração de Atendimento ao Cliente** impulsionada por Inteligência Artificial. Projetada para escalar, reduzir custos operacionais e oferecer suporte 24/7 através de múltiplos canais.

---

## 📋 Sumário
- [Visão Geral](#-visão-geral)
- [Arquitetura da Solução](#-arquitetura-da-solução)
- [Stack Tecnológica](#-stack-tecnológica)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Guia de Instalação (Local)](#-guia-de-instalação-local)
- [Deploy na Azure](#-deploy-na-azure)
- [Documentação da API](#-documentação-da-api)
- [Estrutura do Projeto](#-estrutura-do-projeto)

---

## 🌟 Visão Geral

Este projeto foi desenvolvido para o **Hackathon Microsoft Innovation Challenge (Novembro 2025)**. Ele resolve o problema de gargalos em centrais de atendimento tradicionais, onde agentes humanos perdem tempo com triagem e dúvidas repetitivas.

### A Solução
Um sistema híbrido que utiliza IA para:
1.  **Classificar** automaticamente a intenção do cliente.
2.  **Resolver** demandas simples (ex: 2ª via de boleto, status de pedido) sem intervenção humana.
3.  **Encaminhar** casos complexos para filas especializadas com todo o contexto já coletado.

---

## 🏗️ Arquitetura da Solução

A aplicação segue uma arquitetura **Monolítica Modular**, otimizada para deploy simplificado na Azure App Service, mas mantendo separação clara de responsabilidades.

```mermaid
graph TD
    Client[Cliente / Frontend] -->|HTTPS| AzureApp[Azure App Service]
    
    subgraph "Azure App Service (Linux)"
        FastAPI[Backend FastAPI]
        React[Frontend React (Static)]
        FastAPI -->|Serve| React
    end
    
    FastAPI -->|Persistência| DB[(Azure Database for PostgreSQL)]
    FastAPI -->|Autenticação| JWT[JWT Auth Service]
    FastAPI -->|Classificação| AI[AI Service Module]
```

---

## 🛠️ Stack Tecnológica

### Backend (API & Core)
-   **Linguagem**: Python 3.10+
-   **Framework**: FastAPI (Alta performance, assíncrono)
-   **ORM**: SQLAlchemy 2.0 (Async/Sync)
-   **Validação**: Pydantic V2
-   **Autenticação**: OAuth2 com JWT (JSON Web Tokens)

### Frontend (Interface)
-   **Framework**: React 18
-   **Build Tool**: Vite
-   **Estilização**: CSS Modules / Glassmorphism UI
-   **Router**: React Router v6

### Infraestrutura & DevOps
-   **Cloud**: Microsoft Azure (App Service + PostgreSQL Flexible Server)
-   **CI/CD**: GitHub Actions (Pipeline automatizado de Build & Deploy)
-   **Containerização**: Docker (para desenvolvimento local)

---

## ✨ Funcionalidades Principais

### 1. Portal de Autoatendimento (`/support`)
-   **Acesso Público**: Interface amigável para clientes abrirem chamados.
-   **Chat Widget com IA**: Bot flutuante para consulta rápida de status de tickets.
-   **Geração de Boletos**: Módulo de autoatendimento para emissão de 2ª via de faturas.
-   **Segurança**: Fluxos segregados para clientes e não-clientes (tratativa de leads).

### 2. Painel Administrativo (`/dashboard`)
-   **Métricas em Tempo Real**: KPIs de volume de chamados, taxa de resolução por IA e novos clientes.
-   **Gestão de Tickets**: Kanban/Lista para agentes humanos tratarem casos escalados.
-   **Gestão de Clientes**: CRM básico para cadastro e histórico de clientes.

### 3. Inteligência Artificial
-   **Classificação Automática**: Analisa o texto da solicitação e define a categoria (Financeiro, Suporte Técnico, Vendas).
-   **Respostas Sugeridas**: A IA propõe respostas baseadas em histórico e base de conhecimento.

---

## 🚀 Guia de Instalação (Local)

### Pré-requisitos
-   Python 3.10+
-   Node.js 18+
-   PostgreSQL

### Passo 1: Backend
```bash
# Clone o repositório
git clone https://github.com/Jcnok/central-atendimento-azure.git
cd central-atendimento-azure

# Crie o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure o .env (use o .env.example como base)
cp .env.example .env

# Inicie o servidor
uvicorn src.main:app --reload
```

### Passo 2: Frontend
```bash
cd frontend

# Instale as dependências
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```
Acesse: `http://localhost:5173`

---

## ☁️ Deploy na Azure

O projeto conta com um pipeline de CI/CD configurado em `.github/workflows/deploy.yml`.

1.  **Infraestrutura**: Crie um **Web App (App Service)** e um **PostgreSQL Flexible Server** na Azure.
2.  **Configuração**: No App Service, vá em *Settings > Configuration* e adicione as variáveis de ambiente (`DATABASE_URL`, `SECRET_KEY`, etc.).
3.  **Deploy**: Qualquer push na branch `master` dispara o build do React, o setup do Python e o deploy automático.

---

## 📚 Documentação da API

A documentação interativa (Swagger UI) é gerada automaticamente pelo FastAPI.

-   **Local**: `http://localhost:8000/docs`
-   **Produção**: `https://seu-app.azurewebsites.net/docs`

### Endpoints Principais

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Autenticação de administradores |
| `POST` | `/api/chamados/public` | Abertura de chamado (Público) |
| `GET` | `/api/chamados/public/{id}` | Consulta de status (Chat Widget) |
| `POST` | `/api/boletos/gerar` | Geração de 2ª via de boleto |
| `GET` | `/api/metricas` | Dados para o Dashboard (Admin) |

---

## 📁 Estrutura do Projeto

```
central-atendimento-azure/
├── .github/workflows/    # Pipelines de CI/CD
├── frontend/             # Aplicação React (Vite)
│   ├── src/
│   │   ├── components/   # Componentes Reutilizáveis (ChatWidget, Layout)
│   │   ├── pages/        # Páginas (Dashboard, Support, Login)
│   │   └── context/      # Gestão de Estado (Auth)
├── src/                  # Backend FastAPI
│   ├── routes/           # Controladores de API
│   ├── models/           # Modelos de Banco de Dados
│   ├── schemas/          # Schemas Pydantic (DTOs)
│   └── main.py           # Entrypoint da Aplicação
├── tests/                # Testes Automatizados (Pytest)
└── requirements.txt      # Dependências Python
```

---

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---
**Desenvolvido com 💙 por Julio Okuda**