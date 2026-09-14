from collections.abc import Generator

from sqlalchemy.orm import Session

from backend.app.db.db import SessionLocal


def obter_sessao() -> Generator[Session, None, None]:
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()
