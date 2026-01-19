"""Migración limpia con CuentaPago

Revision ID: b089eff2cd2e
Revises: <PONÉ_ACÁ_TU_REVISION_ANTERIOR>
Create Date: 2025-11-01 11:04:35.786246
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers
revision = 'b089eff2cd2e'
down_revision = '67de8065027f'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # ---------- cuenta_pago ----------
    columnas_cuenta = [c['name'] for c in inspector.get_columns('cuenta_pago')]

    with op.batch_alter_table('cuenta_pago', schema=None) as batch_op:
        if 'email' not in columnas_cuenta:
            batch_op.add_column(sa.Column('email', sa.String(120)))

        if 'public_key' not in columnas_cuenta:
            batch_op.add_column(sa.Column('public_key', sa.String(200)))

        if 'access_token' not in columnas_cuenta:
            batch_op.add_column(sa.Column('access_token', sa.String(200)))

        if 'alias' in columnas_cuenta:
            batch_op.drop_column('alias')

        if 'cbu' in columnas_cuenta:
            batch_op.drop_column('cbu')

    # ---------- order ----------
    columnas_order = [c['name'] for c in inspector.get_columns('order')]
    fks_order = [fk['name'] for fk in inspector.get_foreign_keys('order')]

    with op.batch_alter_table('order', schema=None) as batch_op:
        if 'cuenta_pago_id' not in columnas_order:
            batch_op.add_column(sa.Column('cuenta_pago_id', sa.Integer()))

        if 'estado_pago' not in columnas_order:
            batch_op.add_column(sa.Column('estado_pago', sa.String(50)))

        if 'fk_order_cuenta_pago' not in fks_order:
            batch_op.create_foreign_key(
                'fk_order_cuenta_pago',
                'cuenta_pago',
                ['cuenta_pago_id'],
                ['id']
            )


def downgrade():
    # ❗ En producción NO usamos downgrade destructivo
    pass