"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-01-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('auth0_id', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('picture', sa.String(500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('subscription_tier', sa.Enum('free', 'patriot', 'watchdog', 'founder', name='subscriptiontier'), nullable=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_author', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_auth0_id', 'users', ['auth0_id'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Articles table
    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('slug', sa.String(500), nullable=False),
        sa.Column('subtitle', sa.String(500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('pillar', sa.Enum('money_trail', 'sanctuary', 'loopholes', 'border_complex', 'impact', name='contentpillar'), nullable=False),
        sa.Column('tags', sa.String(500), nullable=True),
        sa.Column('tier_required', sa.Enum('free', 'patriot', 'watchdog', 'founder', name='subscriptiontier'), nullable=True),
        sa.Column('status', sa.Enum('draft', 'published', 'archived', name='articlestatus'), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('view_count', sa.Integer(), nullable=False, default=0),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('cover_image_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['author_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_articles_id', 'articles', ['id'])
    op.create_index('ix_articles_slug', 'articles', ['slug'], unique=True)

    # Subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=False),
        sa.Column('stripe_price_id', sa.String(255), nullable=False),
        sa.Column('tier', sa.Enum('free', 'patriot', 'watchdog', 'founder', name='subscriptiontier'), nullable=False),
        sa.Column('status', sa.Enum('active', 'canceled', 'past_due', 'incomplete', 'trialing', name='subscriptionstatus'), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscriptions_id', 'subscriptions', ['id'])
    op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'], unique=True)

    # FOIA Requests table
    op.create_table(
        'foia_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('agency', sa.String(255), nullable=False),
        sa.Column('agency_contact', sa.String(500), nullable=True),
        sa.Column('topic', sa.Text(), nullable=False),
        sa.Column('request_text', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'submitted', 'acknowledged', 'processing', 'partial_response', 'completed', 'denied', 'appealed', 'withdrawn', name='foiastatus'), nullable=True),
        sa.Column('tracking_number', sa.String(255), nullable=True),
        sa.Column('request_date', sa.Date(), nullable=True),
        sa.Column('expected_response_date', sa.Date(), nullable=True),
        sa.Column('actual_response_date', sa.Date(), nullable=True),
        sa.Column('follow_up_date', sa.Date(), nullable=True),
        sa.Column('response_notes', sa.Text(), nullable=True),
        sa.Column('denial_reason', sa.Text(), nullable=True),
        sa.Column('related_article_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['related_article_id'], ['articles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_foia_requests_id', 'foia_requests', ['id'])

    # Source Documents table
    op.create_table(
        'source_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('document_type', sa.Enum('pdf', 'image', 'spreadsheet', 'text', 'video', 'other', name='documenttype'), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('s3_key', sa.String(500), nullable=True),
        sa.Column('external_url', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=False),
        sa.Column('tier_required', sa.Enum('free', 'patriot', 'watchdog', 'founder', name='subscriptiontier'), nullable=True),
        sa.Column('source_name', sa.String(255), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('document_date', sa.DateTime(), nullable=True),
        sa.Column('article_id', sa.Integer(), nullable=True),
        sa.Column('foia_request_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id']),
        sa.ForeignKeyConstraint(['foia_request_id'], ['foia_requests.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_source_documents_id', 'source_documents', ['id'])


def downgrade() -> None:
    op.drop_table('source_documents')
    op.drop_table('foia_requests')
    op.drop_table('subscriptions')
    op.drop_table('articles')
    op.drop_table('users')
    
    op.execute('DROP TYPE IF EXISTS documenttype')
    op.execute('DROP TYPE IF EXISTS foiastatus')
    op.execute('DROP TYPE IF EXISTS subscriptionstatus')
    op.execute('DROP TYPE IF EXISTS articlestatus')
    op.execute('DROP TYPE IF EXISTS contentpillar')
    op.execute('DROP TYPE IF EXISTS subscriptiontier')
