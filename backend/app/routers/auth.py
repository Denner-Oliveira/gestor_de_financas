from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import (
    criar_refresh_token,
    criar_token_acesso,
    gerar_hash_senha,
    hash_refresh_token,
    verificar_senha,
)
from backend.app.db.dependencies import obter_sessao
from backend.app.models.models import ContaFinanceira, RefreshToken, Usuario
from backend.app.schemas.schemas import (
    RefreshTokenRequest,
    TokenResposta,
    UsuarioCriar,
    UsuarioResposta,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registrar", response_model=UsuarioResposta, status_code=201)
def registrar(dados: UsuarioCriar, sessao: Session = Depends(obter_sessao)):
    existente = sessao.scalar(select(Usuario).where(Usuario.email == dados.email))
    if existente:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")

    usuario = Usuario(
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
    )
    sessao.add(usuario)
    sessao.commit()
    sessao.refresh(usuario)
    sessao.add(
        ContaFinanceira(
            usuario_id=usuario.id,
            nome="Dinheiro em espécie",
            banco="Não se aplica",
            tipo="dinheiro",
        )
    )
    sessao.commit()
    return usuario


@router.post("/login", response_model=TokenResposta)
def login(
    formulario: OAuth2PasswordRequestForm = Depends(),
    sessao: Session = Depends(obter_sessao),
):
    usuario = sessao.scalar(select(Usuario).where(Usuario.email == formulario.username))
    if usuario is None or not verificar_senha(formulario.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    refresh_token, token_hash = criar_refresh_token()
    sessao.add(
        RefreshToken(
            usuario_id=usuario.id,
            token_hash=token_hash,
            expira_em=datetime.now(timezone.utc) + timedelta(days=30),
        )
    )
    sessao.commit()
    return TokenResposta(
        access_token=criar_token_acesso(usuario.id),
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResposta)
def refresh(dados: RefreshTokenRequest, sessao: Session = Depends(obter_sessao)):
    token = sessao.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(dados.refresh_token),
            RefreshToken.revogado_em.is_(None),
        )
    )
    expira_em = (
        token.expira_em.replace(tzinfo=timezone.utc)
        if token is not None and token.expira_em.tzinfo is None
        else token.expira_em if token is not None else None
    )
    if token is None or expira_em <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado.")

    token.revogado_em = datetime.now(timezone.utc)
    novo_refresh, novo_hash = criar_refresh_token()
    sessao.add(
        RefreshToken(
            usuario_id=token.usuario_id,
            token_hash=novo_hash,
            expira_em=datetime.now(timezone.utc) + timedelta(days=30),
        )
    )
    sessao.commit()
    return TokenResposta(
        access_token=criar_token_acesso(token.usuario_id),
        refresh_token=novo_refresh,
    )


@router.post("/logout", status_code=204)
def logout(dados: RefreshTokenRequest, sessao: Session = Depends(obter_sessao)):
    token = sessao.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(dados.refresh_token),
            RefreshToken.revogado_em.is_(None),
        )
    )
    if token:
        token.revogado_em = datetime.now(timezone.utc)
        sessao.commit()
