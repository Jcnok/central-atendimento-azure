# Usar uma imagem base oficial do Python. A versão 'slim' é mais leve.
FROM python:3.10-slim

# Definir variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema, se necessário (ex: para psycopg2)
# Neste caso, a imagem slim já contém o necessário, mas é uma boa prática deixar a linha comentada.
# RUN apt-get update && apt-get install -y ...

# Copiar o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação para o diretório de trabalho
COPY . .

# Expor a porta que a aplicação irá rodar.
# O Gunicorn será configurado para usar a porta 8000.
EXPOSE 8000

# Comando para iniciar a aplicação quando o container for executado.
# Usamos Gunicorn para um ambiente de produção.
# O comando é o mesmo do startup.sh, mas sem a necessidade de especificar o bind,
# pois o docker-compose fará o mapeamento da porta.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:8000"]
