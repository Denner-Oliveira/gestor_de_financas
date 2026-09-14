"""Create the initial finance schema.

Revision ID: 20260914_1200
Revises:
Create Date: 2026-09-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260914_1200"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=False)

    op.create_table(
        "contas_financeiras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("banco", sa.String(length=100), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("ativa", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "tipo IN ('cartao_credito', 'cartao_debito', 'conta_corrente', 'conta_poupanca', 'dinheiro')",
            name="ck_contas_financeiras_tipo",
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contas_financeiras_usuario", "contas_financeiras", ["usuario_id"], unique=False)

    op.create_table(
        "compras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("conta_id", sa.Integer(), nullable=True),
        sa.Column("descricao", sa.String(length=200), nullable=False),
        sa.Column("categoria", sa.String(length=80), nullable=False),
        sa.Column("valor_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("quantidade_parcelas", sa.Integer(), nullable=False),
        sa.Column("data_compra", sa.Date(), nullable=False),
        sa.Column("forma_pagamento", sa.String(length=10), server_default="pix", nullable=False),
        sa.Column("observacoes", sa.String(length=500), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("valor_total > 0", name="ck_compras_valor_total_positivo"),
        sa.CheckConstraint("quantidade_parcelas > 0", name="ck_compras_parcelas_positiva"),
        sa.CheckConstraint("forma_pagamento IN ('pix', 'debito', 'boleto', 'deposito', 'dinheiro', 'credito')", name="ck_compras_forma_pagamento"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["conta_id"], ["contas_financeiras.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_compras_usuario_data", "compras", ["usuario_id", "data_compra"], unique=False)

    op.create_table(
        "parcelas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("compra_id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("valor", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("data_vencimento", sa.Date(), nullable=False),
        sa.Column("data_pagamento", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.CheckConstraint("numero > 0", name="ck_parcelas_numero_positivo"),
        sa.CheckConstraint("valor > 0", name="ck_parcelas_valor_positivo"),
        sa.CheckConstraint("status IN ('pendente', 'paga', 'cancelada')", name="ck_parcelas_status"),
        sa.ForeignKeyConstraint(["compra_id"], ["compras.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("compra_id", "numero", name="uq_parcelas_compra_numero"),
    )
    op.create_index("ix_parcelas_vencimento", "parcelas", ["data_vencimento"], unique=False)

    op.create_table(
        "receitas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("conta_id", sa.Integer(), nullable=True),
        sa.Column("descricao", sa.String(length=200), nullable=False),
        sa.Column("categoria", sa.String(length=80), nullable=False),
        sa.Column("valor", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("forma_recebimento", sa.String(length=10), server_default="pix", nullable=False),
        sa.Column("observacoes", sa.String(length=500), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("valor > 0", name="ck_receitas_valor_positivo"),
        sa.CheckConstraint("forma_recebimento IN ('pix', 'debito', 'boleto', 'deposito', 'dinheiro', 'credito')", name="ck_receitas_forma_recebimento"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["conta_id"], ["contas_financeiras.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_receitas_usuario_data", "receitas", ["usuario_id", "data"], unique=False)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revogado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_refresh_tokens_usuario_id", "refresh_tokens", ["usuario_id"], unique=False)
    op.execute(
        sa.text(
            "INSERT INTO contas_financeiras "
            "(usuario_id, nome, banco, tipo, ativa) "
            "SELECT id, 'Dinheiro em espécie', 'Não se aplica', 'dinheiro', 1 "
            "FROM usuarios "
            "WHERE NOT EXISTS ("
            "SELECT 1 FROM contas_financeiras cf "
            "WHERE cf.usuario_id = usuarios.id AND cf.tipo = 'dinheiro'"
            ")"
        )
    )


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_usuario_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_receitas_usuario_data", table_name="receitas")
    op.drop_table("receitas")
    op.drop_index("ix_parcelas_vencimento", table_name="parcelas")
    op.drop_table("parcelas")
    op.drop_index("ix_compras_usuario_data", table_name="compras")
    op.drop_table("compras")
    op.drop_index("ix_contas_financeiras_usuario", table_name="contas_financeiras")
    op.drop_table("contas_financeiras")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")
