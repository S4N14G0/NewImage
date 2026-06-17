"""agregar descuento_transferencia a configuracion

Revision ID: 794569c53f93
Revises: b089eff2cd2e
Create Date: 2026-06-16 20:41:46.943957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '794569c53f93'
down_revision = 'b089eff2cd2e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('configuracion', schema=None) as batch_op:
        batch_op.add_column(sa.Column('descuento_transferencia', sa.Float(), nullable=False, server_default='0.05'))


def downgrade():
    with op.batch_alter_table('configuracion', schema=None) as batch_op:
        batch_op.drop_column('descuento_transferencia')

    # ### end Alembic commands ###
