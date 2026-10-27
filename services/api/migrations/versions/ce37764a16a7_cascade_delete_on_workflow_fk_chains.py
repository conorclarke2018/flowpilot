"""cascade delete on workflow fk chains

Revision ID: ce37764a16a7
Revises: 7f94158673bc
Create Date: 2026-10-27 16:29:04.018333

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ce37764a16a7'
down_revision: Union[str, Sequence[str], None] = '7f94158673bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('approvals_workflow_run_id_fkey', 'approvals', type_='foreignkey')
    op.create_foreign_key(
        'approvals_workflow_run_id_fkey', 'approvals', 'workflow_runs',
        ['workflow_run_id'], ['id'], ondelete='CASCADE',
    )
    op.drop_constraint('node_runs_workflow_run_id_fkey', 'node_runs', type_='foreignkey')
    op.create_foreign_key(
        'node_runs_workflow_run_id_fkey', 'node_runs', 'workflow_runs',
        ['workflow_run_id'], ['id'], ondelete='CASCADE',
    )
    op.drop_constraint('workflow_runs_workflow_id_fkey', 'workflow_runs', type_='foreignkey')
    op.create_foreign_key(
        'workflow_runs_workflow_id_fkey', 'workflow_runs', 'workflows',
        ['workflow_id'], ['id'], ondelete='CASCADE',
    )
    op.drop_constraint('workflow_versions_workflow_id_fkey', 'workflow_versions', type_='foreignkey')
    op.create_foreign_key(
        'workflow_versions_workflow_id_fkey', 'workflow_versions', 'workflows',
        ['workflow_id'], ['id'], ondelete='CASCADE',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('workflow_versions_workflow_id_fkey', 'workflow_versions', type_='foreignkey')
    op.create_foreign_key(
        'workflow_versions_workflow_id_fkey', 'workflow_versions', 'workflows',
        ['workflow_id'], ['id'],
    )
    op.drop_constraint('workflow_runs_workflow_id_fkey', 'workflow_runs', type_='foreignkey')
    op.create_foreign_key(
        'workflow_runs_workflow_id_fkey', 'workflow_runs', 'workflows',
        ['workflow_id'], ['id'],
    )
    op.drop_constraint('node_runs_workflow_run_id_fkey', 'node_runs', type_='foreignkey')
    op.create_foreign_key(
        'node_runs_workflow_run_id_fkey', 'node_runs', 'workflow_runs',
        ['workflow_run_id'], ['id'],
    )
    op.drop_constraint('approvals_workflow_run_id_fkey', 'approvals', type_='foreignkey')
    op.create_foreign_key(
        'approvals_workflow_run_id_fkey', 'approvals', 'workflow_runs',
        ['workflow_run_id'], ['id'],
    )
