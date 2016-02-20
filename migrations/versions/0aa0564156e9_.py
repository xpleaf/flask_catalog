"""empty message

Revision ID: 0aa0564156e9
Revises: None
Create Date: 2016-02-18 11:12:48.214921

"""

# revision identifiers, used by Alembic.
revision = '0aa0564156e9'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('company', sa.String(length=100), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'company')
    ### end Alembic commands ###
