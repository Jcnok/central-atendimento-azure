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

## ☁️ Deploy na Azure: Guia Completo

Esta seção fornece um guia detalhado para fazer o deploy da aplicação e do banco de dados no Azure.

### Pré-requisitos

1.  **Conta no Azure**: Você precisa de uma assinatura ativa. [Crie uma gratuitamente](https://azure.microsoft.com/free/).
2.  **Azure CLI**: Instale a interface de linha de comando do Azure. [Guia de instalação](https://docs.microsoft.com/cli/azure/install-azure-cli).
3.  **Código no GitHub**: O seu código deve estar em um repositório GitHub para facilitar o deploy contínuo.

Após instalar a Azure CLI, faça o login:
```bash
az login
```

### Passo 1: Criar o Banco de Dados (Azure Database for PostgreSQL)

A aplicação precisa de um banco de dados PostgreSQL. Vamos criar um usando o "Servidor Flexível", que é a opção recomendada.

<details>
<summary><strong>Opção 1: Criar Banco de Dados com Azure CLI (Recomendado)</strong></summary>

```bash
# Variáveis (sinta-se à vontade para alterar os nomes)
RESOURCE_GROUP="central-atendimento-rg" # Usar o nome do seu grupo de recursos existente
LOCATION="canadacentral" # Usar a localização do seu grupo de recursos existente
POSTGRES_SERVER_NAME="pg-central-atendimento-$RANDOM"
POSTGRES_DB_NAME="central_atendimento_db"
ADMIN_USER="dbadmin"
ADMIN_PASSWORD="SuaSenhaSuperForte123!" # ATENÇÃO: Use uma senha forte e segura!

# 1. Criar um Grupo de Recursos (se ainda não tiver um com o nome acima)
# az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Criar o servidor PostgreSQL
# A SKU B_Standard_B1ms é uma das mais baratas, ideal para dev/teste.
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

# 3. Criar o banco de dados dentro do servidor
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $POSTGRES_SERVER_NAME \
  --database-name $POSTGRES_DB_NAME

# 4. Obter a string de conexão (será usada no Passo 3)
# Anote o resultado deste comando!
az postgres flexible-server show-connection-string \
  --server-name $POSTGRES_SERVER_NAME \
  --database-name $POSTGRES_DB_NAME \
  --admin-user $ADMIN_USER \
  --admin-password $ADMIN_PASSWORD
```
</details>

<details>
<summary><strong>Opção 2: Criar Banco de Dados com o Portal Azure</strong></summary>

1.  No portal do Azure, clique em **"Criar um recurso"**.
2.  Procure por **"Banco de Dados do Azure para PostgreSQL"** e clique em "Criar".
3.  Selecione a opção **"Servidor Flexível"**.
4.  Preencha os detalhes:
    -   **Grupo de Recursos**: Selecione o seu grupo de recursos existente (ex: `central-atendimento-rg`).
    -   **Nome do servidor**: Escolha um nome único globalmente (ex: `pg-central-atendimento-seu-nome`).
    -   **Região**: Escolha a mesma região do seu grupo de recursos (ex: `Canada Central`).
    -   **Computação + armazenamento**: Clique em "Configurar servidor" e escolha o nível "Expansível" (`Burstable`), com a SKU `B1ms` para manter os custos baixos.
    -   **Nome de usuário do administrador** e **Senha**: Crie suas credenciais.
5.  Vá para a aba **"Rede"**.
    -   Em "Método de conectividade", selecione **"Acesso público"**.
    -   Em "Regras de firewall", clique em **"Permitir acesso público de qualquer serviço do Azure..."**. Isso é crucial para que o App Service consiga se conectar.
6.  Clique em **"Revisar + criar"** e depois em **"Criar"**.
7.  Após a criação do servidor, vá até o recurso, clique em **"Bancos de Dados"** no menu lateral e crie um novo banco de dados (ex: `central_atendimento_db`).
</details>

### Passo 2: Deploy da Aplicação (Azure App Service)

Agora, vamos fazer o deploy da aplicação FastAPI.

<details>
<summary><strong>Opção 1: Deploy com Azure CLI (Recomendado)</strong></summary>

O comando `az webapp up` é uma forma poderosa de criar e fazer o deploy de uma vez só.

```bash
# Execute este comando na raiz do seu projeto

# Variáveis
RESOURCE_GROUP="central-atendimento-rg" # Usar o nome do seu grupo de recursos existente
LOCATION="canadacentral" # Usar a localização do seu grupo de recursos existente
WEBAPP_NAME="app-central-atendimento-$RANDOM" # Nome único para sua aplicação web

# 1. Registrar o provedor Microsoft.Web (se ainda não estiver registrado)
#    Isso é necessário para criar App Services.
az provider register --namespace Microsoft.Web

# 2. Criar o App Service Plan e o App Service, e fazer o deploy do código
#    O comando detecta automaticamente que é um projeto Python.
az webapp up \
  --resource-group $RESOURCE_GROUP \
  --name $WEBAPP_NAME \
  --sku B1 \
  --location $LOCATION
```
Este comando pode demorar alguns minutos. Ele irá configurar um deploy básico. Anote o `WEBAPP_NAME` gerado, pois ele será usado na configuração do CI/CD.
</details>

<details>
<summary><strong>Opção 2: Deploy com o Portal Azure e GitHub</strong></summary>

1.  No portal do Azure, clique em **"Criar um recurso"**.
2.  Procure por **"Aplicativo Web"** (`Web App`) e clique em "Criar".
3.  Preencha os detalhes:
    -   **Grupo de Recursos**: Selecione o seu grupo de recursos existente (ex: `central-atendimento-rg`).
    -   **Nome**: Escolha um nome único globalmente (ex: `app-central-atendimento-seu-nome`).
    -   **Publicar**: `Código`.
    -   **Pilha de runtime**: `Python 3.10` (ou a versão que estiver usando).
    -   **Sistema Operacional**: `Linux`.
    -   **Região**: Escolha a mesma região do seu grupo de recursos (ex: `Canada Central`).
    -   **Plano do Serviço de Aplicativo**: Crie um novo. A SKU `B1` (Básico) é uma boa opção de baixo custo para começar.
4.  Clique em **"Revisar + criar"** e depois em **"Criar"**.
5.  Após a criação, vá até o recurso do App Service.
6.  No menu lateral, vá para **"Centro de Implantação"** (`Deployment Center`).
7.  Selecione **"GitHub"** como a fonte.
8.  Autorize o Azure a acessar seu GitHub e selecione o repositório e o branch (ex: `master` ou `main`) do seu projeto.
9.  Salve a configuração. O Azure irá automaticamente buscar seu código e iniciar o primeiro deploy (CI/CD).
</details>

### Passo 3: Configurar Variáveis de Ambiente no App Service

Sua aplicação não lê o arquivo `.env` em produção. As variáveis de ambiente devem ser configuradas diretamente no App Service.

1.  Vá para o seu recurso de **App Service** no portal do Azure.
2.  No menu lateral, vá para **"Configuração"** (`Configuration`).
3.  Na aba **"Configurações do aplicativo"** (`Application settings`), clique em **"+ Nova configuração de aplicativo"** para adicionar as seguintes variáveis:

| Nome da Configuração | Valor | Descrição |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://dbadmin:SuaSenhaSuperForte123!@pg-central-atendimento-xxxx.postgres.database.azure.com:5432/central_atendimento_db` | A string de conexão do seu banco de dados PostgreSQL. |
| `SECRET_KEY` | `SuaChaveSecretaSuperLongaGeradaComOpenSSL` | A mesma chave secreta que você usaria localmente. |
| `ALGORITHM` | `HS256` | Opcional, já é o padrão. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Opcional, já é o padrão. |

4.  **Comando de Inicialização**: Ainda na página de "Configuração", vá para a aba **"Configurações gerais"** (`General settings`).
    -   No campo **"Comando de inicialização"** (`Startup Command`), insira o comando Gunicorn para produção:
        ```
        gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
        ```
5.  **Salve as alterações!** O App Service será reiniciado com as novas configurações.

### Passo 4: Acessar a Aplicação

Após a reinicialização, sua API estará no ar!

-   Vá para a página de **"Visão geral"** (`Overview`) do seu App Service.
-   Você encontrará a URL padrão do seu site (ex: `https://app-central-atendimento-xxxx.azurewebsites.net`).
-   Acesse a documentação em `https://<sua-url>/docs` para começar a interagir com a sua API em produção.

---

## 🚀 Configurando CI/CD com GitHub Actions

Automatize o deploy da sua aplicação no Azure App Service a cada push para a branch `master` (ou `main`).

### Pré-requisitos

1.  **Repositório GitHub**: Seu código deve estar no GitHub.
2.  **App Service no Azure**: O App Service para onde você fará o deploy já deve estar criado e configurado (conforme a seção [Deploy na Azure](#-deploy-na-azure)).
3.  **Azure CLI**: Instalada e logada localmente.

### Passo 1: Criar um Service Principal no Azure

Um Service Principal é uma identidade de segurança que o GitHub Actions usará para se autenticar no Azure e realizar o deploy.

1.  **Obtenha o ID da sua assinatura Azure**:
    ```bash
    az account show --query "{id:id, name:name}"
    ```
    Anote o valor do `id`.

2.  **Crie o Service Principal**: Substitua `{seu-subscription-id}` pelo ID da sua assinatura e `central-atendimento-rg` pelo nome do seu grupo de recursos.

    ```bash
    az ad sp create-for-rbac --name "sp-central-atendimento-github" --role "contributor" --scopes "/subscriptions/{seu-subscription-id}/resourceGroups/central-atendimento-rg" --sdk-auth
    ```
    <details>
    <summary><strong>Solução de Problemas: `ResourceGroupNotFound`</strong></summary>
    Se você receber o erro `ResourceGroupNotFound`, significa que o grupo de recursos especificado não existe ou o nome está incorreto. Verifique o nome do seu grupo de recursos no Portal do Azure ou crie-o primeiro com `az group create --name "central-atendimento-rg" --location "canadacentral"`.
    </details>

3.  **Copie o JSON de Saída**: O comando irá gerar um bloco JSON com as credenciais do Service Principal. **Copie todo este bloco**, pois ele será usado no próximo passo.

### Passo 2: Configurar o Segredo no GitHub

Armazene as credenciais do Service Principal de forma segura no seu repositório GitHub.

1.  No seu repositório GitHub, vá para **"Settings" > "Secrets and variables" > "Actions"**.
2.  Clique em **"New repository secret"**.
3.  **Name**: `AZURE_CREDENTIALS` (use este nome exato).
4.  **Secret**: Cole todo o bloco JSON copiado do terminal.
5.  Clique em **"Add secret"**.

### Passo 3: Criar o Arquivo de Workflow (`.github/workflows/deploy.yml`)

Este arquivo define o pipeline de CI/CD.

1.  No seu repositório local, crie a pasta `.github/workflows/` (se não existir).
2.  Dentro dela, crie um arquivo chamado `deploy.yml`.
3.  Cole o seguinte conteúdo no arquivo, **substituindo `app-central-atendimento-19055` pelo nome real do seu App Service**:

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches:
      - master # Ou 'main', dependendo do nome da sua branch principal

env:
  AZURE_WEBAPP_NAME: app-central-atendimento-19055 # Substitua pelo nome do seu App Service
  PYTHON_VERSION: '3.10' # Versão do Python usada no seu projeto

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python ${{ env.PYTHON_VERSION }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest
      env: # Variáveis de ambiente dummy para os testes
        DATABASE_URL: "postgresql://test:test@localhost/testdb"
        SECRET_KEY: "test_secret_key_for_ci"

    - name: Log in to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ env.AZURE_WEBAPP_NAME }}
        slot-name: 'production'
        package: . # Implanta o conteúdo do diretório raiz do repositório
        startup-command: 'gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app'
```

### Passo 4: Commit e Push

1.  Adicione o arquivo `deploy.yml` ao Git, faça o commit e envie para a branch `master`:
    ```bash
    git add .github/workflows/deploy.yml
    git commit -m "feat(ci): Adicionar pipeline de CI/CD para Azure App Service"
    git push origin master
    ```
2.  **Monitore o Deploy**: Vá para a aba **"Actions"** do seu repositório no GitHub para acompanhar o progresso do pipeline.

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
