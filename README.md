# 🎯 Central de Atendimento Automática com IA

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green?logo=fastapi)
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
- [🚀 Começando: Guia de Instalação](#-começando-guia-de-instalação)
- [⚙️ Variáveis de Ambiente](#-variáveis-de-ambiente)
- [📡 Testando a API: Guia Prático](#-testando-a-api-guia-prático)
- [🤔 Solução de Problemas (Troubleshooting)](#-solução-de-problemas-troubleshooting)
- [🧪 Testes Automatizados](#-testes-automatizados)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [☁️ Deploy na Azure](#-deploy-na-azure)
- [📈 Roadmap](#-roadmap)
- [📝 Licença e Contato](#-licença-e-contato)

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

## 🚀 Começando: Guia de Instalação

Siga os passos abaixo para ter o projeto rodando localmente.

#### 1. Pré-requisitos

-   [Python 3.10+](https://www.python.org/)
-   [Git](https://git-scm.com/)
-   Um servidor PostgreSQL rodando (localmente ou na nuvem).

#### 2. Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Jcnok/central-atendimento-azure.git
cd central-atendimento-azure

# 2. Crie e ative um ambiente virtual
# No Linux/macOS
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

#### 3. Configuração do Ambiente

A aplicação precisa de variáveis de ambiente para rodar.

```bash
# Copie o arquivo de exemplo. Este será seu arquivo de configuração local.
cp .env.example .env
```
Agora, **abra o arquivo `.env`** e preencha as variáveis obrigatórias. Veja a seção [Variáveis de Ambiente](#-variáveis-de-ambiente) para mais detalhes. No mínimo, você precisará configurar `DATABASE_URL` e `SECRET_KEY`.

#### 4. Execução

Com tudo configurado, inicie a aplicação:
```bash
# Inicie o servidor em modo de desenvolvimento com auto-reload
uvicorn src.main:app --reload
```
A API estará disponível em `http://127.0.0.1:8000`. As tabelas do banco de dados são criadas automaticamente na primeira inicialização.

---

## ⚙️ Variáveis de Ambiente

As configurações são carregadas do arquivo `.env`.

| Variável | Obrigatório? | Descrição | Exemplo |
| :--- | :---: | :--- | :--- |
| `DATABASE_URL` | **Sim** | String de conexão com o PostgreSQL. | `postgresql://user:pass@host:port/db` |
| `SECRET_KEY` | **Sim** | Chave secreta para assinar os tokens JWT. | `uma_chave_super_secreta_e_segura` |
| `ALGORITHM` | Não | Algoritmo de assinatura do token JWT. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | Tempo de expiração do token de acesso. | `30` |

<details>
<summary><strong>Dica de Segurança para a SECRET_KEY</strong></summary>

Nunca use chaves fracas ou exemplos em produção. Para gerar uma chave forte e aleatória, use o seguinte comando no seu terminal e copie o resultado para a sua variável `SECRET_KEY` no arquivo `.env`:

```bash
openssl rand -hex 32
```
</details>

---

## 📡 Testando a API: Guia Prático

Para interagir com os endpoints, especialmente os protegidos, siga este guia passo a passo usando a documentação interativa do Swagger UI.

1.  **Acesse a Documentação**
    -   Com a aplicação rodando, abra o seu navegador em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

2.  **Crie uma Conta de Usuário**
    -   Vá até o endpoint `POST /auth/signup`.
    -   Clique em "Try it out".
    -   Preencha o `username`, `email` e `password` no corpo da requisição e clique em "Execute".
    -   Você deve receber uma resposta com um `access_token`. **Você não precisa copiar este token inicial.**

3.  **Autorize sua Sessão no Swagger UI**
    -   No topo da página, clique no botão verde **"Authorize"**.
    -   Uma janela pop-up chamada "Available authorizations" aparecerá.
    -   No formulário, digite o `username` e `password` que você acabou de criar.
    -   **Ignore os campos `client_id` e `client_secret`**. Eles não são usados neste projeto.
    -   Clique no botão azul **"Authorize"** na parte inferior da janela.
    -   Pode fechar a janela (botão "Close"). Agora você verá um ícone de cadeado fechado, indicando que sua sessão está autenticada.

4.  **Teste um Endpoint Protegido**
    -   Agora você pode testar qualquer endpoint protegido, como `POST /clientes/`.
    -   Clique em "Try it out", preencha os dados de um cliente e clique em "Execute".
    -   A requisição agora será enviada com o cabeçalho de autorização correto, e você deve receber uma resposta `201 Created`.

---

## 🤔 Solução de Problemas (Troubleshooting)

<details>
<summary><strong>Erro: `column "alguma_coluna" of relation "alguma_tabela" does not exist`</strong></summary>

-   **Causa:** Este erro acontece quando o seu código foi atualizado (ex: uma nova coluna foi adicionada a um modelo), mas o esquema do seu banco de dados não foi. A aplicação tenta usar uma coluna que não existe na sua tabela antiga.
-   **Solução:** Para ambientes de desenvolvimento, a solução mais rápida é resetar o banco de dados.
    1.  Pare a aplicação (CTRL+C).
    2.  Execute o script `reset_db.py` que acompanha o projeto:
        ```bash
        python reset_db.py
        ```
    3.  Reinicie a aplicação. **Lembre-se que isso apagará todos os seus dados**, e você precisará criar um novo usuário.
</details>

<details>
<summary><strong>Erro: `NameError: name 'ConfigDict' is not defined` ou `SECRET_KEY Field required`</strong></summary>

-   **Causa:** Um erro de inicialização que geralmente indica uma dependência faltando ou uma variável de ambiente não configurada.
-   **Solução:**
    1.  Verifique se você criou o arquivo `.env` e preencheu a `DATABASE_URL` e a `SECRET_KEY`.
    2.  Garanta que todas as dependências foram instaladas corretamente executando `pip install -r requirements.txt`.
</details>

---

## 🧪 Testes Automatizados

O projeto utiliza **Pytest** para testes automatizados. Os testes rodam em um banco de dados **SQLite em memória**, garantindo que sejam rápidos e não afetem os dados de desenvolvimento.

Para executar a suíte de testes completa:
```bash
pytest
```

---

## 📁 Estrutura do Projeto

A estrutura do código é organizada por responsabilidades para facilitar a manutenção.
```
central-atendimento-azure/
├── src/
│   ├── main.py                # Ponto de entrada da aplicação FastAPI
│   ├── config/
│   │   ├── database.py        # Configuração da engine e sessão SQLAlchemy
│   │   └── settings.py        # Configurações Pydantic (carregadas do .env)
│   ├── models/                # Modelos ORM do SQLAlchemy (tabelas)
│   ├── schemas/               # Schemas Pydantic (validação de dados da API)
│   ├── routes/                # Endpoints da API (rotas)
│   └── services/              # Lógica de negócio (ex: classificação com IA)
├── tests/                     # Testes automatizados
├── .env.example               # Arquivo de exemplo para variáveis de ambiente
├── requirements.in            # Dependências diretas do projeto
├── requirements.txt           # Dependências travadas (gerado por pip-tools)
├── pyproject.toml             # Configuração de ferramentas (Black, Ruff)
└── reset_db.py                # Script para resetar o banco de dados de dev
```

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
