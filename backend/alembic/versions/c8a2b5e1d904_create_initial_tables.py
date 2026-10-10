"""create_initial_tables

Revision ID: c8a2b5e1d904
Revises: 
Create Date: 2026-10-10 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8a2b5e1d904'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema:
    Creates base tables (users, documents, chat_history, insights).
    Safe for fresh databases and idempotent for existing schemas.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    # 1. users table
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('password_hash', sa.String(), nullable=False),
            sa.Column('role', sa.String(), server_default='Enterprise Member', nullable=True),
            sa.Column('plan', sa.String(), server_default='Enterprise Pro', nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('last_login', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. documents table (initial base schema without error_message)
    if 'documents' not in existing_tables:
        op.create_table(
            'documents',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('filename', sa.String(), nullable=False),
            sa.Column('file_path', sa.String(), nullable=False),
            sa.Column('file_size', sa.String(), server_default='0 MB', nullable=True),
            sa.Column('page_count', sa.Integer(), server_default='1', nullable=True),
            sa.Column('chunk_count', sa.Integer(), server_default='1', nullable=True),
            sa.Column('category', sa.String(), server_default='General', nullable=True),
            sa.Column('status', sa.String(), server_default='READY', nullable=True),
            sa.Column('processing_progress', sa.Integer(), server_default='100', nullable=True),
            sa.Column('processed_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # 3. chat_history table
    if 'chat_history' not in existing_tables:
        op.create_table(
            'chat_history',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('document_id', sa.String(), nullable=False),
            sa.Column('question', sa.Text(), nullable=False),
            sa.Column('answer', sa.Text(), nullable=False),
            sa.Column('sources', sa.JSON(), nullable=True),
            sa.Column('timestamp', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # 4. insights table
    if 'insights' not in existing_tables:
        op.create_table(
            'insights',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('document_id', sa.String(), nullable=False),
            sa.Column('summary', sa.Text(), nullable=False),
            sa.Column('topics', sa.JSON(), nullable=True),
            sa.Column('entities', sa.JSON(), nullable=True),
            sa.Column('key_takeaways', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('document_id')
        )


def downgrade() -> None:
    """
    Downgrade schema:
    Drops base tables in reverse dependency order.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'insights' in existing_tables:
        op.drop_table('insights')
    if 'chat_history' in existing_tables:
        op.drop_table('chat_history')
    if 'documents' in existing_tables:
        op.drop_table('documents')
    if 'users' in existing_tables:
        indexes = [idx['name'] for idx in inspector.get_indexes('users')]
        if 'ix_users_email' in indexes:
            op.drop_index(op.f('ix_users_email'), table_name='users')
        op.drop_table('users')
