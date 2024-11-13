"""Fixed LongText to Text

Revision ID: d023b927b943
Revises: 571e7e3fd314
Create Date: 2024-11-08 15:59:47.904115

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd023b927b943'
down_revision = '571e7e3fd314'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Chat',
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_table('ChatLine',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('chat_text', sa.Text(), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['Chat.chat_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['Users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('UserMealPlan')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UserMealPlan',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=256), nullable=True),
    sa.Column('calories', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('macros', mysql.JSON(), nullable=True),
    sa.Column('ingredients', mysql.JSON(), nullable=True),
    sa.Column('directions', mysql.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['Users.user_id'], name='UserMealPlan_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('ChatLine')
    op.drop_table('Chat')
    # ### end Alembic commands ###
