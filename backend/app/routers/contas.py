from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.core.security import obter_usuario_atual
from backend.app.db.dependencies import obter_sessao
from backend.app.models.models import Compra, ContaFinanceira, Receita, Usuario
from backend.app.schemas.schemas import ContaFinanceiraCriar, ContaFinanceiraAtualizar, ContaFinanceiraResposta

router = APIRouter(tags=['financeiro'])

def _validar_conta(
    conta_id: int,
    usuario_id: int,
    sessao: Session,
) -> ContaFinanceira:
    conta = sessao.scalar(
        select(ContaFinanceira).where(
            ContaFinanceira.id == conta_id,
            ContaFinanceira.usuario_id == usuario_id,
            ContaFinanceira.ativa.is_(True),
        )
    )
    if conta is None:
        raise HTTPException(status_code=404, detail="Conta financeira não encontrada.")
    return conta


@router.post(
    "/contas",
    response_model=ContaFinanceiraResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_conta(
    dados: ContaFinanceiraCriar,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    conta = ContaFinanceira(**dados.model_dump(), usuario_id=usuario.id)
    sessao.add(conta)
    sessao.commit()
    sessao.refresh(conta)
    return conta


@router.get("/contas", response_model=list[ContaFinanceiraResposta])
def listar_contas(
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    return list(
        sessao.scalars(
            select(ContaFinanceira)
            .where(
                ContaFinanceira.usuario_id == usuario.id,
                ContaFinanceira.ativa.is_(True),
            )
            .order_by(ContaFinanceira.banco, ContaFinanceira.nome)
        )
    )



@router.patch("/contas/{conta_id}", response_model=ContaFinanceiraResposta)
def atualizar_conta(
    conta_id: int,
    dados: ContaFinanceiraAtualizar,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    conta = _validar_conta(conta_id, usuario.id, sessao)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(conta, campo, valor)
    sessao.commit()
    sessao.refresh(conta)
    return conta


@router.delete("/contas/{conta_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_conta(
    conta_id: int,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    conta = _validar_conta(conta_id, usuario.id, sessao)
    possui_receitas = sessao.scalar(
        select(Receita.id).where(Receita.conta_id == conta_id).limit(1)
    )
    possui_compras = sessao.scalar(
        select(Compra.id).where(Compra.conta_id == conta_id).limit(1)
    )
    if possui_receitas is not None or possui_compras is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir uma conta que possui movimentações.",
        )
    sessao.delete(conta)
    sessao.commit()
