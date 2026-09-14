"""Remove duplicated payment method fields.

Revision ID: 20260914_1202
Revises: 20260914_1201
Create Date: 2026-09-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260914_1202"
down_revision = "20260914_1201"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("compras") as batch_op:
        batch_op.drop_column("forma_pagamento")
    with op.batch_alter_table("receitas") as batch_op:
        batch_op.drop_column("forma_recebimento")


def downgrade() -> None:
    with op.batch_alter_table("compras") as batch_op:
        batch_op.add_column(
            sa.Column("forma_pagamento", sa.String(length=10), nullable=False, server_default="pix"),
        )
    with op.batch_alter_table("receitas") as batch_op:
        batch_op.add_column(
            sa.Column("forma_recebimento", sa.String(length=10), nullable=False, server_default="pix"),
        )
