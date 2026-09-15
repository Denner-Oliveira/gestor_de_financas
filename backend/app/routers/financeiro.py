"""Agregador dos routers financeiros.

As rotas continuam sob o mesmo prefixo público (sem prefixo adicional);
este módulo existe para manter compatibilidade com imports existentes.
"""

from fastapi import APIRouter

from backend.app.routers import contas, importacoes, lancamentos, relatorios

router = APIRouter()
router.include_router(contas.router)
router.include_router(lancamentos.router)
router.include_router(relatorios.router)
router.include_router(importacoes.router)
