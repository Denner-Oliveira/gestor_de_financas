from datetime import date
from decimal import Decimal, ROUND_DOWN

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.core.security import obter_usuario_atual
from backend.app.db.dependencies import obter_sessao
from backend.app.models.models import (
    Compra,
    ContaFinanceira,
    Parcela,
    Receita,
    Usuario,
)
from backend.app.schemas.schemas import (
    ContaFinanceiraCriar,
    ContaFinanceiraAtualizar,
    ContaFinanceiraResposta,
    CompraCriar,
    CompraAtualizar,
    CompraResposta,
    ReceitaAtualizar,
    ReceitaCriar,
    ReceitaResposta,
)


router = APIRouter(tags=["financeiro"])


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


@router.post("/receitas", response_model=ReceitaResposta, status_code=status.HTTP_201_CREATED)
def criar_receita(
    dados: ReceitaCriar,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    _validar_conta(dados.conta_id, usuario.id, sessao)
    receita = Receita(**dados.model_dump(), usuario_id=usuario.id)
    sessao.add(receita)
    sessao.commit()
    sessao.refresh(receita)
    return receita


@router.get("/receitas", response_model=list[ReceitaResposta])
def listar_receitas(
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
    ano: int | None = None,
    mes: int | None = None,
    conta_id: int | None = None,
):
    if mes is not None and not 1 <= mes <= 12:
        raise HTTPException(status_code=422, detail="O mês deve estar entre 1 e 12.")
    filtros = [Receita.usuario_id == usuario.id]
    if ano is not None and mes is not None:
        inicio = date(ano, mes, 1)
        fim = date(ano + (mes == 12), 1 if mes == 12 else mes + 1, 1)
        filtros.extend([Receita.data >= inicio, Receita.data < fim])
    elif ano is not None:
        filtros.extend([Receita.data >= date(ano, 1, 1), Receita.data < date(ano + 1, 1, 1)])
    if conta_id is not None:
        filtros.append(Receita.conta_id == conta_id)
    return list(
        sessao.scalars(
            select(Receita)
            .where(*filtros)
            .order_by(Receita.data.desc())
        )
    )


@router.patch("/receitas/{receita_id}", response_model=ReceitaResposta)
def atualizar_receita(
        receita_id: int,
        dados: ReceitaAtualizar,
        usuario: Usuario = Depends(obter_usuario_atual),
        sessao: Session = Depends(obter_sessao),
):
        receita = sessao.scalar(
            select(Receita).where(
                Receita.id == receita_id, Receita.usuario_id == usuario.id
            )
        )
        if receita is None:
            raise HTTPException(status_code=404, detail="Receita não encontrada.")
        if dados.conta_id is not None:
            _validar_conta(dados.conta_id, usuario.id, sessao)
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(receita, campo, valor)
        sessao.commit()
        sessao.refresh(receita)
        return receita


@router.delete("/receitas/{receita_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_receita(
        receita_id: int,
        usuario: Usuario = Depends(obter_usuario_atual),
        sessao: Session = Depends(obter_sessao),
):
        receita = sessao.scalar(
            select(Receita).where(
                Receita.id == receita_id, Receita.usuario_id == usuario.id
            )
        )
        if receita is None:
            raise HTTPException(status_code=404, detail="Receita não encontrada.")
        sessao.delete(receita)
        sessao.commit()


@router.post("/compras", response_model=CompraResposta, status_code=status.HTTP_201_CREATED)
def criar_compra(
    dados: CompraCriar,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    _validar_conta(dados.conta_id, usuario.id, sessao)
    valor_parcela = (dados.valor_total / dados.quantidade_parcelas).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    valores = [valor_parcela] * dados.quantidade_parcelas
    valores[-1] += dados.valor_total - sum(valores)

    compra = Compra(**dados.model_dump(), usuario_id=usuario.id)
    compra.parcelas = [
        Parcela(
            numero=numero,
            valor=valor,
            data_vencimento=dados.data_compra + relativedelta(months=numero - 1),
        )
        for numero, valor in enumerate(valores, start=1)
    ]
    sessao.add(compra)
    sessao.commit()
    sessao.refresh(compra)
    return compra


@router.get("/compras", response_model=list[CompraResposta])
def listar_compras(
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
    ano: int | None = None,
    mes: int | None = None,
    conta_id: int | None = None,
):
    if mes is not None and not 1 <= mes <= 12:
        raise HTTPException(status_code=422, detail="O mês deve estar entre 1 e 12.")
    filtros = [Compra.usuario_id == usuario.id]
    if conta_id is not None:
        filtros.append(Compra.conta_id == conta_id)
    if ano is not None and mes is not None:
        inicio = date(ano, mes, 1)
        fim = date(ano + (mes == 12), 1 if mes == 12 else mes + 1, 1)
        filtros.extend([Parcela.data_vencimento >= inicio, Parcela.data_vencimento < fim])
    elif ano is not None:
        filtros.extend(
            [
                Parcela.data_vencimento >= date(ano, 1, 1),
                Parcela.data_vencimento < date(ano + 1, 1, 1),
            ]
        )
    consulta = select(Compra).options(selectinload(Compra.parcelas))
    if ano is not None or mes is not None:
        consulta = consulta.join(Compra.parcelas)
    consulta = consulta.where(*filtros).order_by(Compra.data_compra.desc())
    resultado = sessao.scalars(consulta)
    return list(resultado.unique())


@router.patch("/compras/{compra_id}", response_model=CompraResposta)
def atualizar_compra(
        compra_id: int,
        dados: CompraAtualizar,
        usuario: Usuario = Depends(obter_usuario_atual),
        sessao: Session = Depends(obter_sessao),
):
        compra = sessao.scalar(
            select(Compra)
            .options(selectinload(Compra.parcelas))
            .where(Compra.id == compra_id, Compra.usuario_id == usuario.id)
        )
        if compra is None:
            raise HTTPException(status_code=404, detail="Compra não encontrada.")

        alteracoes = dados.model_dump(exclude_unset=True)
        if dados.conta_id is not None:
            _validar_conta(dados.conta_id, usuario.id, sessao)
        parcelas_pagas = any(parcela.status == "paga" for parcela in compra.parcelas)
        campos_estruturais = {"valor_total", "quantidade_parcelas", "data_compra"}
        if parcelas_pagas and campos_estruturais.intersection(alteracoes):
            raise HTTPException(
                status_code=409,
                detail="Não é possível alterar valores ou parcelas após um pagamento.",
            )

        for campo, valor in alteracoes.items():
            setattr(compra, campo, valor)

        if campos_estruturais.intersection(alteracoes):
            valor_parcela = (compra.valor_total / compra.quantidade_parcelas).quantize(
                Decimal("0.01"), rounding=ROUND_DOWN
            )
            valores = [valor_parcela] * compra.quantidade_parcelas
            valores[-1] += compra.valor_total - sum(valores)
            compra.parcelas = [
                Parcela(
                    numero=numero,
                    valor=valor,
                    data_vencimento=compra.data_compra + relativedelta(months=numero - 1),
                )
                for numero, valor in enumerate(valores, start=1)
            ]

        sessao.commit()
        sessao.refresh(compra)
        return compra


@router.delete("/compras/{compra_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_compra(
        compra_id: int,
        usuario: Usuario = Depends(obter_usuario_atual),
        sessao: Session = Depends(obter_sessao),
):
        compra = sessao.scalar(
            select(Compra).where(
                Compra.id == compra_id, Compra.usuario_id == usuario.id
            )
        )
        if compra is None:
            raise HTTPException(status_code=404, detail="Compra não encontrada.")
        sessao.delete(compra)
        sessao.commit()
