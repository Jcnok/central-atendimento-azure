#!/bin/bash

# Script de inicialização para Azure App Service

echo "🚀 Iniciando Central de Atendimento Automática..."

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
python -c "from src.config.database import init_db; init_db()"

echo "✅ Aplicação pronta para rodar!"

# Iniciar Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:8000
