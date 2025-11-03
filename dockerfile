# Dockerfile
FROM python:3.11-slim

#Define o diretório de trabalho dentro do conteiner
WORKDIR /app

# copia e Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código para o diretorio de trabalho
COPY . .

# Expõe porta que rodará o uvicorn
EXPOSE 8000

# Comando para Rodar o app com uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]