"""create_document_chunks_table

Revision ID: 9bb703bbe849
Revises: 43192b8456eb
Create Date: 2026-10-10 22:02:30.714937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bb703bbe849'
down_revision: Union[str, Sequence[str], None] = '43192b8456eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'document_chunks' not in existing_tables:
        op.create_table('document_chunks',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('document_id', sa.String(), nullable=False),
            sa.Column('chunk_index', sa.Integer(), nullable=False),
            sa.Column('page_number', sa.Integer(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('metadata_json', sa.Text(), nullable=True),
            sa.Column('embedding_json', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)

    # Optional native pgvector acceleration for Neon PostgreSQL
    if bind.dialect.name == "postgresql":
        try:
            # Check if vector extension is available in PostgreSQL
            res = bind.execute(sa.text("SELECT count(*) FROM pg_available_extensions WHERE name = 'vector';")).scalar()
            if res and res > 0:
                bind.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector;"))
                columns = [c['name'] for c in inspector.get_columns('document_chunks')]
                if 'embedding' not in columns:
                    bind.execute(sa.text("ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS embedding vector(768);"))
                print("[Alembic] Successfully enabled pgvector extension and verified embedding vector(768) column.")
        except Exception as e:
            print(f"[Alembic] Notice on pgvector (fallback to JSON vector store): {e}")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'document_chunks' in existing_tables:
        if bind.dialect.name == "postgresql":
            try:
                bind.execute(sa.text("ALTER TABLE document_chunks DROP COLUMN IF EXISTS embedding;"))
            except Exception:
                pass

        indexes = [idx['name'] for idx in inspector.get_indexes('document_chunks')]
        if 'ix_document_chunks_document_id' in indexes:
            op.drop_index(op.f('ix_document_chunks_document_id'), table_name='document_chunks')
        op.drop_table('document_chunks')
