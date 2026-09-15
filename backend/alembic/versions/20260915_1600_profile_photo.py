"""Add profile photo fields.

Revision ID: 20260915_1600
Revises: 20260914_1203
"""

from alembic import op
import sqlalchemy as sa


revision = "20260915_1600"
down_revision = "20260914_1203"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("foto_perfil", sa.LargeBinary(), nullable=True))
    op.add_column("usuarios", sa.Column("foto_perfil_tipo", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("usuarios", "foto_perfil_tipo")
    op.drop_column("usuarios", "foto_perfil")
