from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)

class Base(DeclarativeBase):
    """Classe base para os modelos persistidos pelo SQLAlchemy."""


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    compras: Mapped[list["Compra"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    receitas: Mapped[list["Receita"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
    contas: Mapped[list["ContaFinanceira"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
    )


class ContaFinanceira(Base):
    __tablename__ = "contas_financeiras"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('cartao_credito', 'cartao_debito', 'conta_corrente', "
            "'conta_poupanca', 'dinheiro')",
            name="ck_contas_financeiras_tipo",
        ),
        Index("ix_contas_financeiras_usuario", "usuario_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    banco: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    ativa: Mapped[bool] = mapped_column(nullable=False, default=True)

    usuario: Mapped[Usuario] = relationship(back_populates="contas")
    compras: Mapped[list["Compra"]] = relationship(back_populates="conta")
    receitas: Mapped[list["Receita"]] = relationship(back_populates="conta")

class Compra(Base):
    __tablename__ = "compras"
    __table_args__ = (
        CheckConstraint("valor_total > 0", name="ck_compras_valor_total_positivo"),
        CheckConstraint("quantidade_parcelas > 0", name="ck_compras_parcelas_positiva"),
        Index("ix_compras_usuario_data", "usuario_id", "data_compra"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    conta_id: Mapped[int | None] = mapped_column(
        ForeignKey("contas_financeiras.id", ondelete="RESTRICT")
    )
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantidade_parcelas: Mapped[int] = mapped_column(nullable=False, default=1)
    data_compra: Mapped[date] = mapped_column(Date, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(String(500))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    usuario: Mapped[Usuario] = relationship(back_populates="compras")
    conta: Mapped[ContaFinanceira | None] = relationship(back_populates="compras")
    parcelas: Mapped[list["Parcela"]] = relationship(
        back_populates="compra",
        cascade="all, delete-orphan",
        order_by="Parcela.numero",
    )

class Parcela(Base):
    __tablename__ = "parcelas"
    __table_args__ = (
        UniqueConstraint("compra_id", "numero", name="uq_parcelas_compra_numero"),
        CheckConstraint("numero > 0", name="ck_parcelas_numero_positivo"),
        CheckConstraint("valor > 0", name="ck_parcelas_valor_positivo"),
        CheckConstraint(
            "status IN ('pendente', 'paga', 'cancelada')",
            name="ck_parcelas_status",
        ),
        Index("ix_parcelas_vencimento", "data_vencimento"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    compra_id: Mapped[int] = mapped_column(
        ForeignKey("compras.id", ondelete="CASCADE"),
        nullable=False,
    )
    numero: Mapped[int] = mapped_column(nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_pagamento: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="pendente",
    )

    compra: Mapped[Compra] = relationship(back_populates="parcelas")

class Receita(Base):
    __tablename__ = "receitas"
    __table_args__ = (
        CheckConstraint("valor > 0", name="ck_receitas_valor_positivo"),
        Index("ix_receitas_usuario_data", "usuario_id", "data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    conta_id: Mapped[int | None] = mapped_column(
        ForeignKey("contas_financeiras.id", ondelete="RESTRICT")
    )
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    categoria: Mapped[str] = mapped_column(String(80), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(String(500))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    usuario: Mapped[Usuario] = relationship(back_populates="receitas")
    conta: Mapped[ContaFinanceira | None] = relationship(back_populates="receitas")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revogado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False
    )

    usuario: Mapped[Usuario] = relationship()