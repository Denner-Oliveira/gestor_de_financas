from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.email import enviar_email_recuperacao
from backend.app.core.security import (
    criar_token_temporario,
    criar_refresh_token,
    criar_token_acesso,
    gerar_hash_senha,
    hash_refresh_token,
    obter_usuario_atual,
    verificar_senha,
)
from backend.app.db.dependencies import obter_sessao
from backend.app.models.models import (
    ContaFinanceira,
    PasswordResetToken,
    RefreshToken,
    Usuario,
)
from backend.app.schemas.schemas import (
    RefreshTokenRequest,
    RecuperacaoSenhaRedefinir,
    RecuperacaoSenhaSolicitar,
    TokenResposta,
    UsuarioAtualizar,
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


@router.patch("/me", response_model=UsuarioResposta)
def atualizar_usuario(
    dados: UsuarioAtualizar,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    if not verificar_senha(dados.senha_atual, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Senha atual inválida.")
    if dados.email is not None and dados.email != usuario.email:
        existente = sessao.scalar(select(Usuario).where(Usuario.email == dados.email))
        if existente is not None:
            raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
        usuario.email = dados.email
    if dados.nova_senha is not None:
        usuario.senha_hash = gerar_hash_senha(dados.nova_senha)
    sessao.commit()
    sessao.refresh(usuario)
    return usuario


@router.post("/recuperar-senha", status_code=202)
def solicitar_recuperacao(
    dados: RecuperacaoSenhaSolicitar,
    sessao: Session = Depends(obter_sessao),
):
    usuario = sessao.scalar(select(Usuario).where(Usuario.email == dados.email))
    if usuario is not None:
        token, token_hash = criar_token_temporario()
        sessao.add(
            PasswordResetToken(
                usuario_id=usuario.id,
                token_hash=token_hash,
                expira_em=datetime.now(timezone.utc) + timedelta(minutes=30),
            )
        )
        sessao.commit()
        link = f"{settings.frontend_url}/?reset_token={token}"
        try:
            enviar_email_recuperacao(usuario.email, link)
        except RuntimeError as exc:
            sessao.delete(
                sessao.scalar(
                    select(PasswordResetToken).where(
                        PasswordResetToken.token_hash == token_hash
                    )
                )
            )
            sessao.commit()
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"detail": "Se o e-mail estiver cadastrado, enviaremos um link de recuperação."}


@router.post("/redefinir-senha", status_code=204)
def redefinir_senha(
    dados: RecuperacaoSenhaRedefinir,
    sessao: Session = Depends(obter_sessao),
):
    token = sessao.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_refresh_token(dados.token),
            PasswordResetToken.usado_em.is_(None),
        )
    )
    expira_em = (
        token.expira_em.replace(tzinfo=timezone.utc)
        if token is not None and token.expira_em.tzinfo is None
        else token.expira_em if token is not None else None
    )
    if token is None or expira_em <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Link inválido ou expirado.")
    usuario = sessao.get(Usuario, token.usuario_id)
    if usuario is None:
        raise HTTPException(status_code=400, detail="Link inválido ou expirado.")
    usuario.senha_hash = gerar_hash_senha(dados.nova_senha)
    agora = datetime.now(timezone.utc)
    refresh_tokens = sessao.scalars(
        select(RefreshToken).where(
            RefreshToken.usuario_id == usuario.id,
            RefreshToken.revogado_em.is_(None),
        )
    )
    for refresh_token in refresh_tokens:
        refresh_token.revogado_em = agora
    token.usado_em = agora
    sessao.commit()


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
