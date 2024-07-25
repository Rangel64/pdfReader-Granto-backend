FROM python:3.11-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir --default-timeout=5000 -r requirements.txt

# Instale as dependências do sistema operacional necessárias
RUN apt-get update && \
    apt-get install -y build-essential curl procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instale o Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copie o resto do código da aplicação para o diretório de trabalho
COPY . .

# Defina a variável de ambiente para desabilitar o buffer do Python (para melhor logging)
ENV PYTHONUNBUFFERED=1

# Inicie o Ollama
# RUN ollama serve

# Execute o Ollama (isso pode variar dependendo de como você deseja iniciar o serviço)
# RUN ollama run llama3

# Exponha a porta em que a aplicação vai rodar
EXPOSE 8000

# Comando para iniciar a aplicação FastAPI
CMD ["sh", "-c", "ollama serve & hypercorn main:app --bind '[::]:8000'"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]