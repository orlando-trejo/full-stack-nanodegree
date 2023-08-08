"""Added seeking_venue and seeking_description to Artist model

Revision ID: a55e8c96ba36
Revises: e1486366857c
Create Date: 2023-08-08 10:46:28.102371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a55e8c96ba36'
down_revision = 'e1486366857c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seeking_venue', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.drop_column('seeking_description')
        batch_op.drop_column('seeking_venue')

    # ### end Alembic commands ###