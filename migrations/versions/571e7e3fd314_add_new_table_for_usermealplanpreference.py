"""Add new table for UserMealPlanPreference

Revision ID: 571e7e3fd314
Revises: d335300d5e36
Create Date: 2024-11-02 18:02:30.673081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '571e7e3fd314'
down_revision = 'd335300d5e36'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UserMealPlan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=True),
    sa.Column('calories', sa.Integer(), nullable=True),
    sa.Column('macros', sa.JSON(), nullable=True),
    sa.Column('ingredients', sa.JSON(), nullable=True),
    sa.Column('directions', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('UserMealPlan')
    # ### end Alembic commands ###
