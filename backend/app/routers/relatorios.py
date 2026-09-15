from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from backend.app.core.security import obter_usuario_atual
from backend.app.db.dependencies import obter_sessao
from backend.app.models.models import Compra, ContaFinanceira, Parcela, Receita, Usuario

router = APIRouter(tags=['financeiro'])

@router.get("/relatorios/geral")
def relatorio_geral(
    inicio: date,
    fim: date,
    usuario: Usuario = Depends(obter_usuario_atual),
    sessao: Session = Depends(obter_sessao),
):
    if inicio > fim:
        raise HTTPException(
            status_code=422,
            detail="A data inicial deve ser anterior ou igual à data final.",
        )

    receitas = list(
        sessao.scalars(
            select(Receita).where(
                Receita.usuario_id == usuario.id,
                Receita.data >= inicio,
                Receita.data <= fim,
            )
        )
    )
    compras = list(
        sessao.scalars(
            select(Compra)
            .options(selectinload(Compra.parcelas))
            .join(Compra.parcelas)
            .where(
                Compra.usuario_id == usuario.id,
                Parcela.data_vencimento >= inicio,
                Parcela.data_vencimento <= fim,
            )
        ).unique()
    )
    contas = {
        conta.id: conta.nome
        for conta in sessao.scalars(
            select(ContaFinanceira).where(
                ContaFinanceira.usuario_id == usuario.id,
            )
        )
    }

    por_conta: dict[int, dict[str, object]] = {
        conta_id: {"conta": nome, "receitas": Decimal("0"), "despesas": Decimal("0")}
        for conta_id, nome in contas.items()
    }
    por_categoria: dict[str, Decimal] = {}
    por_mes: dict[str, dict[str, Decimal]] = {}

    for receita in receitas:
        conta = por_conta.setdefault(
            receita.conta_id or 0,
            {"conta": "Conta não identificada", "receitas": Decimal("0"), "despesas": Decimal("0")},
        )
        conta["receitas"] += receita.valor
        mes = receita.data.strftime("%Y-%m")
        resumo_mes = por_mes.setdefault(
            mes, {"receitas": Decimal("0"), "despesas": Decimal("0")}
        )
        resumo_mes["receitas"] += receita.valor

    for compra in compras:
        conta = por_conta.setdefault(
            compra.conta_id or 0,
            {"conta": "Conta não identificada", "receitas": Decimal("0"), "despesas": Decimal("0")},
        )
        for parcela in compra.parcelas:
            if inicio <= parcela.data_vencimento <= fim:
                conta["despesas"] += parcela.valor
                por_categoria[compra.categoria] = (
                    por_categoria.get(compra.categoria, Decimal("0")) + parcela.valor
                )
                mes = parcela.data_vencimento.strftime("%Y-%m")
                resumo_mes = por_mes.setdefault(
                    mes, {"receitas": Decimal("0"), "despesas": Decimal("0")}
                )
                resumo_mes["despesas"] += parcela.valor

    total_receitas = sum((receita.valor for receita in receitas), Decimal("0"))
    total_despesas = sum(
        (
            parcela.valor
            for compra in compras
            for parcela in compra.parcelas
            if inicio <= parcela.data_vencimento <= fim
        ),
        Decimal("0"),
    )
    return {
        "inicio": inicio,
        "fim": fim,
        "totais": {
            "receitas": total_receitas,
            "despesas": total_despesas,
            "saldo": total_receitas - total_despesas,
        },
        "por_conta": list(por_conta.values()),
        "por_categoria": [
            {"categoria": categoria, "valor": valor}
            for categoria, valor in sorted(
                por_categoria.items(), key=lambda item: item[1], reverse=True
            )
        ],
        "por_mes": [
            {"mes": mes, **valores}
            for mes, valores in sorted(por_mes.items())
        ],
    }

