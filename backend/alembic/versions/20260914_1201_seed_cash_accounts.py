"""Create the default cash account for existing users.

Revision ID: 20260914_1201
Revises: 20260914_1200
Create Date: 2026-09-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260914_1201"
down_revision = "20260914_1200"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    op.execute(
        sa.text(
            "DELETE FROM contas_financeiras "
            "WHERE tipo = 'dinheiro' "
            "AND nome = 'Dinheiro em espécie' "
            "AND banco = 'Não se aplica'"
        )
    )
