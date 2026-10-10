"""initial_schema_with_error_message

Revision ID: 43192b8456eb
Revises: c8a2b5e1d904
Create Date: 2026-10-10 17:26:21.232151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43192b8456eb'
down_revision: Union[str, Sequence[str], None] = 'c8a2b5e1d904'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema:
    Ensures documents table exists, then adds error_message column if not already present.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'documents' in existing_tables:
        columns = [c['name'] for c in inspector.get_columns('documents')]
        if 'error_message' not in columns:
            op.add_column('documents', sa.Column('error_message', sa.Text(), nullable=True))


def downgrade() -> None:
    """
    Downgrade schema:
    Removes error_message column from documents table.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'documents' in existing_tables:
        columns = [c['name'] for c in inspector.get_columns('documents')]
        if 'error_message' in columns:
            op.drop_column('documents', 'error_message')
