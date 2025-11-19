# 🎯 Central de Atendimento Automática com IA

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green?logo=fastapi)
[![Deploy to Azure App Service](https://github.com/Jcnok/central-atendimento-azure/actions/workflows/deploy.yml/badge.svg)](https://github.com/Jcnok/central-atendimento-azure/actions)
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
- [☁️ Deploy e CI/CD na Azure](#-deploy-e-cicd-na-azure)
- [🤔 Solução de Problemas (Troubleshooting)](#-solução-de-problemas-troubleshooting)
- [🧪 Testes Automatizados](#-testes-automatizados)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
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
| **CI/CD** | GitHub Actions | Automação de testes e deploy. |

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
virtualenv\Scripts\activate

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
    -   Você deve receber uma resposta com um `access_token`. **Você não precisa copiar este token inicial**.

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

## ☁️ Deploy e CI/CD na Azure

Este guia descreve o processo completo para fazer o deploy da aplicação na Azure com um pipeline de CI/CD automatizado usando GitHub Actions.

### Visão Geral do Processo
1.  **Provisionar Recursos na Azure**: Criar a infraestrutura na nuvem (Banco de Dados e App Service).
2.  **Configurar a Conexão Segura**: Criar um Service Principal para permitir que o GitHub se autentique no Azure.
3.  **Configurar o Pipeline**: Apontar o workflow do GitHub Actions para os recursos criados.
4.  **Configurar a Aplicação na Azure**: Adicionar as variáveis de ambiente no App Service.
5.  **Ativar o Pipeline**: Fazer um `push` para a branch `master` para iniciar o deploy.

### Passo 1: Provisionar Recursos na Azure (CLI)

A forma mais rápida de criar os recursos necessários é via Azure CLI.

```bash
# Faça o login na sua conta Azure
az login

# --- CRIE O GRUPO DE RECURSOS E O BANCO DE DADOS ---
# Defina as variáveis para seus recursos
RESOURCE_GROUP="central-atendimento-rg"
LOCATION="canadacentral"
POSTGRES_SERVER_NAME="pg-central-atendimento-$RANDOM"
POSTGRES_DB_NAME="central_atendimento_db"
ADMIN_USER="dbadmin"
ADMIN_PASSWORD="SuaSenhaSuperForte123!" # ATENÇÃO: Use uma senha forte e segura!

# Crie o grupo de recursos
az group create --name $RESOURCE_GROUP --location $LOCATION

# Crie o servidor PostgreSQL Flexível
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER_NAME \
  --location $LOCATION \
  --admin-user $ADMIN_USER \
  --admin-password $ADMIN_PASSWORD \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 32 \
  --version 14

# Crie o banco de dados dentro do servidor
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $POSTGRES_SERVER_NAME \
  --database-name $POSTGRES_DB_NAME

# --- CRIE O APP SERVICE ---
# Defina um nome único para sua aplicação web
WEBAPP_NAME="app-central-atendimento-$RANDOM"

# Registre o provedor de recursos da web (necessário apenas uma vez por assinatura)
az provider register --namespace Microsoft.Web

# Crie o App Service
az webapp up \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --sku B1 \
  --location $LOCATION

# Anote o nome do seu Web App (WEBAPP_NAME) e a string de conexão do banco de dados.
# Você precisará deles nos próximos passos.
```

### Passo 2: Configurar a Conexão Segura (GitHub <> Azure)

1.  **Crie um Service Principal**: Esta é a identidade que o GitHub usará para se autenticar. Substitua `{seu-subscription-id}` e `{seu-grupo-de-recursos}` pelos seus valores.
    ```bash
    # Obtenha seu ID de assinatura
    az account show --query id --output tsv

    # Crie o Service Principal com escopo para o seu grupo de recursos
    az ad sp create-for-rbac \
      --name "sp-central-atendimento-github" \
      --role "contributor" \
      --scopes "/subscriptions/{seu-subscription-id}/resourceGroups/{seu-grupo-de-recursos}" \
      --sdk-auth
    ```
2.  **Copie o JSON de Saída**: O comando acima irá gerar um bloco de código JSON. Copie-o inteiramente.
3.  **Crie um Segredo no GitHub**:
    -   Vá para o seu repositório no GitHub: **Settings > Secrets and variables > Actions**.
    -   Clique em **New repository secret**.
    -   **Name**: `AZURE_CREDENTIALS`
    -   **Secret**: Cole o JSON copiado.
    -   Clique em **Add secret**.

### Passo 3: Configurar o Pipeline de CI/CD

O pipeline já está definido em `.github/workflows/deploy.yml`. Você só precisa ajustá-lo para apontar para o seu App Service.

1.  Abra o arquivo `.github/workflows/deploy.yml`.
2.  Encontre a seção `env` e altere o valor de `AZURE_WEBAPP_NAME` para o nome do App Service que você criou no Passo 1.
    ```yaml
    env:
      AZURE_WEBAPP_NAME: app-central-atendimento-19055 # <-- Altere aqui!
      PYTHON_VERSION: '3.10'
    ```

### Passo 4: Configurar a Aplicação na Azure

O App Service precisa das mesmas variáveis de ambiente que você usa localmente.

1.  Vá para o seu **App Service** no Portal do Azure.
2.  No menu lateral, vá para **Configuration > Application settings**.
3.  Adicione as seguintes configurações:
    -   `DATABASE_URL`: A string de conexão do seu banco de dados PostgreSQL no Azure.
    -   `SECRET_KEY`: A mesma chave secreta forte que você usaria em produção.
4.  Ainda em **Configuration**, vá para a aba **General settings** e defina o **Startup Command**:
    ```
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
    ```
5.  **Salve as alterações**. O App Service será reiniciado.

### Passo 5: Ativar o Pipeline

Faça o commit e o push das alterações que você fez no arquivo `deploy.yml`.

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: Configurar nome do App Service no workflow"
git push origin master
```
Este push irá acionar o pipeline. Vá para a aba **"Actions"** no seu repositório GitHub para acompanhar o deploy. Após a conclusão, sua API estará funcional na URL do Azure.

---

## 🤔 Solução de Problemas (Troubleshooting)

<details>
<summary><strong>Erro local: `column ... does not exist`</strong></summary>

-   **Causa:** Seu banco de dados local está dessincronizado com os modelos da aplicação.
-   **Solução:** Pare a aplicação e execute o script de reset: `python reset_db.py`. **Atenção**: Isso apagará todos os dados locais.
</details>

<details>
<summary><strong>Erro no Azure CLI: `ResourceGroupNotFound`</strong></summary>

-   **Causa:** O grupo de recursos que você especificou em um comando não foi encontrado.
-   **Solução:** Verifique se o nome está correto ou crie o grupo de recursos primeiro com `az group create --name "seu-nome-de-grupo" --location "sua-localizacao"`.
</details>

<details>
<summary><strong>Erro no Azure CLI: `The subscription is not registered to use namespace 'Microsoft.Web'`</strong></summary>

-   **Causa:** Sua assinatura do Azure precisa habilitar o provedor de recursos para criar Aplicativos Web.
-   **Solução:** Execute o comando `az provider register --namespace Microsoft.Web` e aguarde alguns minutos antes de tentar novamente.
</details>

<details>
<summary><strong>Erro no CI/CD: `DATABASE_URL Field required` ou `SECRET_KEY Field required`</strong></summary>

-   **Causa:** O passo de `pytest` no pipeline do GitHub Actions precisa das variáveis de ambiente para inicializar a aplicação, mesmo que os testes usem um banco de dados em memória.
-   **Solução:** O arquivo `deploy.yml` já inclui variáveis de ambiente "dummy" para o passo de teste. Se o erro persistir, verifique se essa configuração foi removida acidentalmente.
</details>

---

## 🧪 Testes Automatizados

Para rodar a suíte de testes localmente e garantir a qualidade do código:
```bash
pytest
```
O pipeline de CI/CD também executa esses testes antes de cada deploy, prevenindo que bugs cheguem à produção.

---

## 📁 Estrutura do Projeto

A estrutura do código é organizada por responsabilidades para facilitar a manutenção.
```
central-atendimento-azure/
├── .github/
│   └── workflows/
│       └── deploy.yml         # Workflow de CI/CD para Azure
├── src/
│   ├── main.py                # Ponto de entrada da aplicação FastAPI
│   ├── config/                # Módulos de configuração (BD, .env)
│   ├── models/                # Modelos ORM do SQLAlchemy (tabelas)
│   ├── schemas/               # Schemas Pydantic (validação de dados da API)
│   ├── routes/                # Endpoints da API (rotas)
│   └── services/              # Lógica de negócio (ex: classificação com IA)
├── tests/                     # Testes automatizados
├── .env.example               # Arquivo de exemplo para variáveis de ambiente
├── requirements.txt           # Dependências travadas (gerado por pip-tools)
└── reset_db.py                # Script para resetar o banco de dados de dev
```

---

## 📈 Roadmap

-   [x] **v1.1**: Autenticação JWT implementada.
-   [x] **v1.2**: Pipeline de CI/CD com GitHub Actions.
-   [ ] **v1.3**: Integração real com **Azure Cognitive Services**, WhatsApp Business API, SendGrid.
-   [ ] **v2.0**: Arquitetura multi-tenant, ML para priorização, integração com CRMs.

---

## 📝 Licença e Contato

Este projeto está sob a licença MIT.

Desenvolvido por **Julio Okuda**.
-   **LinkedIn:** [linkedin.com/in/juliookuda](https://www.linkedin.com/in/juliookuda/)
-   **GitHub:** [@Jcnok](https://github.com/Jcnok)

```