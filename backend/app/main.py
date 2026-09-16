import logging
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from backend.app.core.config import settings
from backend.app.core.logging import configurar_logging
from backend.app.routers import auth, contas, importacoes, lancamentos, relatorios


configurar_logging()
logger = logging.getLogger("backend.app")
access_logger = logging.getLogger("backend.app.access")


app = FastAPI(
    title="Gestor de Finanças API",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth.router)
app.include_router(contas.router)
app.include_router(lancamentos.router)
app.include_router(relatorios.router)
app.include_router(importacoes.router)


@app.middleware("http")
async def registrar_acesso(request: Request, call_next):
    inicio = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duracao_ms = (perf_counter() - inicio) * 1000
        access_logger.error(
            "FALHA | %s %s | status=500 | duracao_ms=%.2f",
            request.method,
            request.url.path,
            duracao_ms,
        )
        logger.exception(
            "Erro não tratado ao processar %s %s.",
            request.method,
            request.url.path,
        )
        raise

    duracao_ms = (perf_counter() - inicio) * 1000
    resultado = "SUCESSO" if response.status_code < 400 else "FALHA"
    access_logger.info(
        "%s | %s %s | status=%s | duracao_ms=%.2f",
        resultado,
        request.method,
        request.url.path,
        response.status_code,
        duracao_ms,
    )
    return response


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}