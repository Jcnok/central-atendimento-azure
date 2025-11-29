#!/bin/bash
# Azure Infrastructure Setup for LLM Agents
# This script provisions all necessary Azure resources for the agent architecture

set -e

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-central-atendimento-rg}"
LOCATION="${LOCATION:-Canada-Central}"
OPENAI_NAME="${OPENAI_NAME:-openai-central-atendimento}"
REDIS_NAME="${REDIS_NAME:-redis-central-atendimento}"
APP_INSIGHTS_NAME="${APP_INSIGHTS_NAME:-appi-central-atendimento}"

echo "🚀 Starting Azure infrastructure setup..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"

# Create Resource Group
echo "📦 Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create Azure OpenAI Service
echo "🤖 Creating Azure OpenAI service..."
az cognitiveservices account create \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --kind OpenAI \
  --sku S0 \
  --custom-domain $OPENAI_NAME

# Deploy GPT-4o model
echo "📊 Deploying GPT-4o model..."
az cognitiveservices account deployment create \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-08-06" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"

# Deploy GPT-4o-mini model
echo "📊 Deploying GPT-4o-mini model..."
az cognitiveservices account deployment create \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"

# Deploy text-embedding-3-small model
echo "📊 Deploying text-embedding-3-small model..."
az cognitiveservices account deployment create \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --deployment-name text-embedding-3-small \
  --model-name text-embedding-3-small \
  --model-version "1" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"

# Create Azure Redis Cache
echo "⚡ Creating Azure Redis Cache..."
az redis create \
  --name $REDIS_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Basic \
  --vm-size C0

# Create Application Insights
echo "📈 Creating Application Insights..."
az monitor app-insights component create \
  --app $APP_INSIGHTS_NAME \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Get connection strings and keys
echo "🔑 Retrieving connection information..."

OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.endpoint" -o tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "key1" -o tsv)

REDIS_HOST=$(az redis show \
  --name $REDIS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "hostName" -o tsv)

REDIS_KEY=$(az redis list-keys \
  --name $REDIS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "primaryKey" -o tsv)

APPINSIGHTS_KEY=$(az monitor app-insights component show \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "instrumentationKey" -o tsv)

# Create .env.agents file
echo "📝 Creating .env.agents configuration file..."
cat > .env.agents <<EOF
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_KEY=$OPENAI_KEY
AZURE_OPENAI_DEPLOYMENT_GPT4O=gpt-4o
AZURE_OPENAI_DEPLOYMENT_GPT4O_MINI=gpt-4o-mini
AZURE_OPENAI_DEPLOYMENT_EMBEDDING=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Azure Redis Configuration
REDIS_HOST=$REDIS_HOST
REDIS_PORT=6380
REDIS_PASSWORD=$REDIS_KEY
REDIS_SSL=true

# Application Insights
APPINSIGHTS_INSTRUMENTATION_KEY=$APPINSIGHTS_KEY

# Agent Configuration
AGENT_MAX_TOKENS=4096
AGENT_TEMPERATURE=0.7
AGENT_CACHE_TTL=3600
EOF

echo "✅ Infrastructure setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.agents to your .env file or source it"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Run database migrations to add pgvector support"
echo "4. Start implementing agents!"
echo ""
echo "💰 Estimated monthly cost: ~$46 (with optimizations)"
