#!/bin/bash

# Script de inicialização para Azure App Service

echo "🚀 Iniciando Gunicorn para a aplicação FastAPI..."

# O Azure App Service injeta a porta na variável de ambiente $PORT.
# O Gunicorn deve escutar nesta porta para que a plataforma consiga
# rotear o tráfego corretamente para a aplicação.
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app --bind "0.0.0.0:$PORT"