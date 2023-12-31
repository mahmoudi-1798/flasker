"""add password field

Revision ID: 5471f020b10d
Revises: 516a71a9837b
Create Date: 2023-08-07 17:16:40.207623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5471f020b10d'
down_revision = '516a71a9837b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###
