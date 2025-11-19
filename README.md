# 🎯 Central de Atendimento Automática com IA

Uma API de back-end robusta para uma central de atendimento, capaz de processar solicitações de múltiplos canais com classificação e resposta por IA.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Deploy to Azure App Service](https://github.com/Jcnok/central-atendimento-azure/actions/workflows/deploy.yml/badge.svg)](https://github.com/Jcnok/central-atendimento-azure/actions)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Visão Geral

Este projeto, desenvolvido para o **Hackathon Microsoft Innovation Challenge**, oferece uma solução escalável para empresas que lidam com um alto volume de solicitações de clientes. A API atua como um orquestrador de atendimento que automatiza o fluxo de trabalho, desde o recebimento e classificação com IA até a resposta automática e o encaminhamento para atendimento humano.

## 🛠️ Tecnologias

| Área | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.10+ | Base da aplicação. |
| **Framework Web** | FastAPI | Alta performance, ASGI. |
| **Banco de Dados** | PostgreSQL | Banco de dados relacional. |
| **ORM** | SQLAlchemy 2.0 | Manipulação de dados segura e assíncrona. |
| **Validação**| Pydantic v2 | Validação de dados e configurações. |
| **Testes** | Pytest | Testes automatizados com banco de dados em memória. |
| **Cloud** | Azure App Service | Hospedagem da aplicação. |
| **CI/CD** | GitHub Actions | Automação de testes e deploy. |

---

## 本地开发环境 (Ambiente de Desenvolvimento Local)

Siga estes passos para executar o projeto na sua máquina local.

### 1. Pré-requisitos
- Python 3.10+
- Git
- Um servidor PostgreSQL rodando (localmente ou em um container Docker).

### 2. Instalação
```bash
# Clone o repositório
git clone https://github.com/Jcnok/central-atendimento-azure.git
cd central-atendimento-azure

# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração do Ambiente
A aplicação carrega as configurações de um arquivo `.env`.

```bash
# Copie o arquivo de exemplo para criar seu arquivo de configuração local
cp .env.example .env
```
**Edite o arquivo `.env`** e configure, no mínimo, as duas variáveis a seguir:

- `DATABASE_URL`: A string de conexão para o seu banco de dados PostgreSQL.
  - Exemplo local: `postgresql://user:password@localhost:5432/nome_do_banco`
- `SECRET_KEY`: Uma chave secreta para assinar os tokens JWT.
  - Para gerar uma chave segura, execute no terminal: `openssl rand -hex 32`

### 4. Execução
```bash
# Inicie o servidor em modo de desenvolvimento com auto-reload
uvicorn src.main:app --reload
```
A API estará disponível em `http://127.0.0.1:8000/docs`.

<details>
<summary><strong>Solução de Problemas Locais</strong></summary>

- **Erro `column ... does not exist`**: Seu banco de dados está dessincronizado com os modelos da aplicação. Para resolver, pare a aplicação e execute o script de reset:
  ```bash
  python reset_db.py
  ```
  **Atenção**: Isso apagará todos os dados do seu banco de dados local.
</details>

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
ADMIN_PASSWORD="SuaSenhaSuperForte123!" # Use uma senha forte!

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
    - Vá para o seu repositório no GitHub: **Settings > Secrets and variables > Actions**.
    - Clique em **New repository secret**.
    - **Name**: `AZURE_CREDENTIALS`
    - **Secret**: Cole o JSON copiado.
    - Clique em **Add secret**.

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
    - `DATABASE_URL`: A string de conexão do seu banco de dados PostgreSQL no Azure.
    - `SECRET_KEY`: A mesma chave secreta forte que você usaria em produção.
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

## 🧪 Testes Automatizados

Para rodar a suíte de testes localmente e garantir a qualidade do código:
```bash
pytest
```
O pipeline de CI/CD também executa esses testes antes de cada deploy, prevenindo que bugs cheguem à produção.