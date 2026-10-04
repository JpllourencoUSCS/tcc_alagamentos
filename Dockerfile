# API FastAPI do backend (serviço "api" do docker-compose.yml, 03/10/2026).
# Mesma imagem serve para qualquer hospedagem que rode contêiner (Render,
# Railway, Fly.io, uma VM) — só muda de onde vêm DATABASE_URL e
# OPENWEATHER_API_KEY.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
# Imports absolutos do projeto (`from constants import ...`) exigem rodar a
# partir de backend/ — mesma convenção do pytest (ver CLAUDE.md)
WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
