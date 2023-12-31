"""Add username

Revision ID: 02738d5e2f5f
Revises: afbf9c769987
Create Date: 2023-08-12 16:15:54.400221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02738d5e2f5f'
down_revision = 'afbf9c769987'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=200), nullable=False))
        batch_op.create_unique_constraint(None, ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('username')

    # ### end Alembic commands ###
