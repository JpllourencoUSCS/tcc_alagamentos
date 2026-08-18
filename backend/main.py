"""
App FastAPI (Semana 3 — Henrique, reconstruído em 18/08/2026).

Rodar localmente (a partir de backend/, para os imports absolutos como
`from constants import ...` resolverem — mesma convenção de fusao_climatica.py):

    cd backend
    uvicorn main:app --reload
"""

from fastapi import FastAPI

from api.ocorrencias import router as ocorrencias_router

app = FastAPI(
    title="Sistema de Monitoramento Colaborativo de Alagamentos",
    version="0.1.0",
)

app.include_router(ocorrencias_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
