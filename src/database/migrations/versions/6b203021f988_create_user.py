"""
create_user

Revision ID: 6b203021f988
Revises: 
Create Date: 2022-07-06 18:01:06.206090
"""
from alembic import op
import sqlalchemy as sa


revision = "6b203021f988"
down_revision = branch_labels = depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email_address', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('is_confirmed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_user_email_address'), 
        'user', 
        ['email_address'], 
        unique=True
    )
    op.create_index(
        op.f('ix_user_id'), 
        'user', 
        ['id'], 
        unique=False
    )
    op.create_index(
        op.f('ix_user_is_confirmed'), 
        'user', 
        ['is_confirmed'], 
        unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_user_is_confirmed'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email_address'), table_name='user')
    op.drop_table('user')
