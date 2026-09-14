from fastapi import FastAPI

from backend.app.routers import auth, financeiro


app = FastAPI(
    title="Gestor de Finanças API",
    version="0.1.0",
)
app.include_router(auth.router)
app.include_router(financeiro.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}