"""Initial migration

Revision ID: 733db9ce1c66
Revises: 
Create Date: 2026-08-21 15:04:17.463750

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '733db9ce1c66'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # crawl_task table
    op.create_table(
        'crawl_task',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('start_url', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('pages_crawled', sa.Integer(), nullable=False),
        sa.Column('pages_failed', sa.Integer(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crawl_task_start_url'), 'crawl_task', ['start_url'], unique=False)

    # page table
    op.create_table(
        'page',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('meta_description', sa.String(), nullable=True),
        sa.Column('canonical_url', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('robots_meta', sa.String(), nullable=True),
        sa.Column('h1_tags', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('h2_tags', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('h3_tags', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('internal_links', sa.ARRAY(sa.String()), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['crawl_task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_page_task_id'), 'page', ['task_id'], unique=False)
    op.create_index(op.f('ix_page_url'), 'page', ['url'], unique=False)

    # seo_issue table
    op.create_table(
        'seo_issue',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('page_id', sa.UUID(), nullable=False),
        sa.Column('rule_id', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('element', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['page_id'], ['page.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seo_issue_page_id'), 'seo_issue', ['page_id'], unique=False)

    # health_issue table
    op.create_table(
        'health_issue',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('issue_type', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['crawl_task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_issue_task_id'), 'health_issue', ['task_id'], unique=False)
    op.create_index(op.f('ix_health_issue_url'), 'health_issue', ['url'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_health_issue_url'), table_name='health_issue')
    op.drop_index(op.f('ix_health_issue_task_id'), table_name='health_issue')
    op.drop_table('health_issue')
    
    op.drop_index(op.f('ix_seo_issue_page_id'), table_name='seo_issue')
    op.drop_table('seo_issue')
    
    op.drop_index(op.f('ix_page_url'), table_name='page')
    op.drop_index(op.f('ix_page_task_id'), table_name='page')
    op.drop_table('page')
    
    op.drop_index(op.f('ix_crawl_task_start_url'), table_name='crawl_task')
    op.drop_table('crawl_task')
